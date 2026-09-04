"""
RoboflowDownloader Module

Handles authentication and download of datasets from Roboflow.
"""

import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class DownloadResult:
    """Result of a dataset download operation."""
    success: bool
    total_images: int
    train_images: int
    valid_images: int
    test_images: int
    download_path: str
    error_message: Optional[str] = None


class RoboflowDownloader:
    """
    Downloads datasets from Roboflow with authentication and retry logic.
    
    This class handles:
    - Roboflow API authentication
    - Dataset downloads in YOLO format
    - Retry logic with exponential backoff
    - Download progress reporting
    """
    
    def __init__(self, api_key: str, dataset_url: str):
        """
        Initialize the downloader with Roboflow credentials.
        
        Args:
            api_key: Roboflow API key for authentication
            dataset_url: Full URL to the Roboflow dataset
                        (e.g., "https://universe.roboflow.com/workspace/project")
        """
        self.api_key = api_key
        self.dataset_url = dataset_url
        self._authenticated = False
        self._rf_client = None
        
    def authenticate(self) -> bool:
        """
        Authenticate with the Roboflow API.
        
        Returns:
            True if authentication succeeds, False otherwise
            
        Raises:
            ImportError: If roboflow package is not installed
            Exception: If authentication fails for other reasons
        """
        try:
            from roboflow import Roboflow
            
            logger.info("Authenticating with Roboflow API...")
            self._rf_client = Roboflow(api_key=self.api_key)
            self._authenticated = True
            logger.info("Authentication successful")
            return True
            
        except ImportError:
            logger.error("Roboflow package not installed. Run: pip install roboflow")
            raise ImportError(
                "Roboflow package is required. Install it with: pip install roboflow"
            )
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            self._authenticated = False
            return False
    
    def download_dataset(
        self, 
        output_dir: str, 
        format: str = "yolov8",
        max_retries: int = 3
    ) -> DownloadResult:
        """
        Download dataset from Roboflow in specified format.
        
        Implements retry logic with exponential backoff for handling
        transient network errors.
        
        Args:
            output_dir: Directory where dataset will be downloaded
            format: Dataset format (default: "yolov8")
            max_retries: Maximum number of download attempts (default: 3)
            
        Returns:
            DownloadResult with download statistics and status
            
        Raises:
            RuntimeError: If not authenticated before calling
            ValueError: If dataset URL is invalid
        """
        if not self._authenticated:
            error_msg = "Not authenticated. Call authenticate() first."
            logger.error(error_msg)
            return DownloadResult(
                success=False,
                total_images=0,
                train_images=0,
                valid_images=0,
                test_images=0,
                download_path="",
                error_message=error_msg
            )
        
        # Validate URL format
        if not self._validate_url():
            error_msg = f"Invalid Roboflow dataset URL: {self.dataset_url}"
            logger.error(error_msg)
            return DownloadResult(
                success=False,
                total_images=0,
                train_images=0,
                valid_images=0,
                test_images=0,
                download_path="",
                error_message=error_msg
            )
        
        # Parse workspace and project from URL
        try:
            workspace, project = self._parse_url()
        except ValueError as e:
            error_msg = f"Failed to parse dataset URL: {str(e)}"
            logger.error(error_msg)
            return DownloadResult(
                success=False,
                total_images=0,
                train_images=0,
                valid_images=0,
                test_images=0,
                download_path="",
                error_message=error_msg
            )
        
        # Attempt download with retry logic
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Download attempt {attempt}/{max_retries}...")
                logger.info(f"Downloading dataset from workspace '{workspace}', project '{project}'")
                
                # Get workspace and project
                workspace_obj = self._rf_client.workspace(workspace)
                project_obj = workspace_obj.project(project)
                
                # Get latest version
                logger.info("Fetching latest dataset version...")
                version = project_obj.version(project_obj.versions()[0])
                
                # Download dataset
                logger.info(f"Downloading dataset in {format} format to {output_dir}...")
                dataset = version.download(format, location=output_dir)
                
                # Count images in each split
                download_path = Path(output_dir) / dataset.name
                stats = self._count_images(download_path)
                
                logger.info(f"Download complete: {stats['total']} total images")
                logger.info(f"  Train: {stats['train']} images")
                logger.info(f"  Valid: {stats['valid']} images")
                logger.info(f"  Test: {stats['test']} images")
                
                return DownloadResult(
                    success=True,
                    total_images=stats['total'],
                    train_images=stats['train'],
                    valid_images=stats['valid'],
                    test_images=stats['test'],
                    download_path=str(download_path)
                )
                
            except Exception as e:
                error_msg = f"Download attempt {attempt} failed: {str(e)}"
                logger.warning(error_msg)
                
                if attempt < max_retries:
                    # Exponential backoff: 2^attempt seconds
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    # Final attempt failed
                    final_error = f"Download failed after {max_retries} attempts: {str(e)}"
                    logger.error(final_error)
                    return DownloadResult(
                        success=False,
                        total_images=0,
                        train_images=0,
                        valid_images=0,
                        test_images=0,
                        download_path="",
                        error_message=final_error
                    )
        
        # Should never reach here, but just in case
        return DownloadResult(
            success=False,
            total_images=0,
            train_images=0,
            valid_images=0,
            test_images=0,
            download_path="",
            error_message="Unknown error occurred"
        )
    
    def _validate_url(self) -> bool:
        """
        Validate that the dataset URL is a valid Roboflow URL.
        
        Returns:
            True if URL is valid, False otherwise
        """
        return (
            self.dataset_url and
            isinstance(self.dataset_url, str) and
            "roboflow.com" in self.dataset_url
        )
    
    def _parse_url(self) -> tuple[str, str]:
        """
        Parse workspace and project names from Roboflow URL.
        
        Expected URL format:
        https://universe.roboflow.com/workspace-name/project-name
        
        Returns:
            Tuple of (workspace, project)
            
        Raises:
            ValueError: If URL cannot be parsed
        """
        try:
            # Remove protocol and domain
            parts = self.dataset_url.replace("https://", "").replace("http://", "")
            parts = parts.split("roboflow.com/")[-1]
            
            # Split into workspace and project
            path_parts = parts.strip("/").split("/")
            
            if len(path_parts) >= 2:
                workspace = path_parts[0]
                project = path_parts[1]
                return workspace, project
            else:
                raise ValueError(f"URL does not contain workspace and project: {self.dataset_url}")
                
        except Exception as e:
            raise ValueError(f"Failed to parse URL: {str(e)}")
    
    def _count_images(self, dataset_path: Path) -> dict:
        """
        Count images in each split of the downloaded dataset.
        
        Args:
            dataset_path: Path to downloaded dataset root
            
        Returns:
            Dictionary with counts for 'train', 'valid', 'test', and 'total'
        """
        counts = {'train': 0, 'valid': 0, 'test': 0}
        
        for split in ['train', 'valid', 'test']:
            images_dir = dataset_path / split / 'images'
            if images_dir.exists():
                # Count image files (jpg, jpeg, png)
                image_extensions = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}
                counts[split] = sum(
                    1 for f in images_dir.iterdir() 
                    if f.is_file() and f.suffix in image_extensions
                )
        
        counts['total'] = sum(counts[split] for split in ['train', 'valid', 'test'])
        return counts
    
    @staticmethod
    def get_api_key_instructions() -> str:
        """
        Return instructions for obtaining a Roboflow API key.
        
        Returns:
            Formatted string with step-by-step instructions
        """
        return """
=== How to Get Your Roboflow API Key ===

Follow these steps to obtain your Roboflow API key:

1. **Sign Up / Log In to Roboflow**
   - Visit: https://app.roboflow.com/
   - Create a free account or log in with your existing account
   - You can sign up with Google, GitHub, or email

2. **Access Your Account Settings**
   - Once logged in, click on your profile icon (top-right corner)
   - Select "Settings" or "Account Settings" from the dropdown menu

3. **Navigate to API Keys**
   - In the settings menu, look for "API Keys" or "Roboflow API"
   - You should see a section labeled "API Key"

4. **Copy Your API Key**
   - Your API key will be displayed as a string of characters
   - Click the "Copy" button to copy it to your clipboard
   - Keep this key secure and do not share it publicly

5. **Use Your API Key**
   - When running the dataset expansion pipeline, provide the API key:
     
     python -m src.dataset_expansion.pipeline --roboflow-api-key YOUR_API_KEY
     
   - Or set it as an environment variable:
     
     export ROBOFLOW_API_KEY=YOUR_API_KEY

**Important Notes:**
- API keys are tied to your account and provide access to private datasets
- Free accounts have usage limits; check Roboflow pricing for details
- If downloading public datasets, you still need an API key for authentication
- Never commit API keys to version control (add to .env or .gitignore)

**Troubleshooting:**
- If you can't find your API key, visit: https://docs.roboflow.com/api-reference/authentication
- For support, contact Roboflow at: support@roboflow.com

==========================================
"""
