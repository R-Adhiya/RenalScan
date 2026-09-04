"""
Basic tests for ClassValidator to verify implementation.
"""

import pytest
import tempfile
from pathlib import Path
from src.dataset_expansion.validators import ClassValidator, ValidationResult


def create_temp_yaml(content: str) -> str:
    """Helper to create temporary YAML file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(content)
        return f.name


def test_parse_classes_list_format():
    """Test parsing class names from list format."""
    yaml_content = """
path: /data
train: train/images
nc: 1
names: ['Kidney Stone']
"""
    yaml_path = create_temp_yaml(yaml_content)
    
    validator = ClassValidator(yaml_path, yaml_path)
    classes = validator.parse_classes(yaml_path)
    
    assert classes == ['Kidney Stone']
    Path(yaml_path).unlink()


def test_parse_classes_dict_format():
    """Test parsing class names from dict format."""
    yaml_content = """
path: /data
train: train/images
nc: 2
names:
  0: stone
  1: background
"""
    yaml_path = create_temp_yaml(yaml_content)
    
    validator = ClassValidator(yaml_path, yaml_path)
    classes = validator.parse_classes(yaml_path)
    
    assert classes == ['stone', 'background']
    Path(yaml_path).unlink()


def test_validate_compatibility_exact_match():
    """Test validation with exact class match."""
    yaml_content = """
names: ['Kidney Stone']
"""
    yaml1 = create_temp_yaml(yaml_content)
    yaml2 = create_temp_yaml(yaml_content)
    
    validator = ClassValidator(yaml1, yaml2)
    result = validator.validate_compatibility()
    
    assert result.is_compatible
    assert not result.needs_remapping
    assert result.current_classes == ['Kidney Stone']
    assert result.source_classes == ['Kidney Stone']
    
    Path(yaml1).unlink()
    Path(yaml2).unlink()


def test_validate_compatibility_semantic_equivalence():
    """Test validation with semantically equivalent stone classes."""
    yaml1_content = """
names: ['Kidney Stone']
"""
    yaml2_content = """
names: ['stone']
"""
    yaml1 = create_temp_yaml(yaml1_content)
    yaml2 = create_temp_yaml(yaml2_content)
    
    validator = ClassValidator(yaml1, yaml2)
    result = validator.validate_compatibility()
    
    assert result.is_compatible
    assert result.needs_remapping
    assert result.mapping == {0: 0}
    
    Path(yaml1).unlink()
    Path(yaml2).unlink()


def test_validate_compatibility_incompatible():
    """Test validation with incompatible classes."""
    yaml1_content = """
names: ['Kidney Stone']
"""
    yaml2_content = """
names: ['cat', 'dog']
"""
    yaml1 = create_temp_yaml(yaml1_content)
    yaml2 = create_temp_yaml(yaml2_content)
    
    validator = ClassValidator(yaml1, yaml2)
    result = validator.validate_compatibility()
    
    assert not result.is_compatible
    assert not result.needs_remapping
    
    Path(yaml1).unlink()
    Path(yaml2).unlink()


def test_create_class_mapping():
    """Test class mapping creation for stone classes."""
    yaml1_content = """
names: ['Kidney Stone']
"""
    yaml2_content = """
names: ['kidney_stone']
"""
    yaml1 = create_temp_yaml(yaml1_content)
    yaml2 = create_temp_yaml(yaml2_content)
    
    validator = ClassValidator(yaml1, yaml2)
    mapping = validator.create_class_mapping()
    
    assert mapping == {0: 0}
    
    Path(yaml1).unlink()
    Path(yaml2).unlink()


def test_remap_labels():
    """Test label remapping functionality."""
    # Create temporary directory for labels
    with tempfile.TemporaryDirectory() as tmpdir:
        label_file = Path(tmpdir) / "test.txt"
        
        # Write YOLO label with class 0
        with open(label_file, 'w') as f:
            f.write("0 0.5 0.5 0.3 0.3\n")
            f.write("0 0.2 0.2 0.1 0.1\n")
        
        # Create dummy validator
        yaml_content = "names: ['stone']"
        yaml_path = create_temp_yaml(yaml_content)
        validator = ClassValidator(yaml_path, yaml_path)
        
        # Remap class 0 to class 1
        mapping = {0: 1}
        validator.remap_labels(tmpdir, mapping)
        
        # Verify remapping
        with open(label_file, 'r') as f:
            lines = f.readlines()
        
        assert lines[0].strip() == "1 0.5 0.5 0.3 0.3"
        assert lines[1].strip() == "1 0.2 0.2 0.1 0.1"
        
        Path(yaml_path).unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
