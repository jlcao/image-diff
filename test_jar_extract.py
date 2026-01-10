#!/usr/bin/env python3
"""
Test script to verify JAR extraction functionality
"""
import os
import zipfile
import shutil
import tempfile

def test_jar_extraction(jar_path):
    """Test JAR extraction and compare with actual JAR contents"""
    print(f"Testing JAR extraction: {jar_path}")
    
    if not os.path.exists(jar_path):
        print(f"ERROR: JAR file not found: {jar_path}")
        return False
    
    # Create temporary directory for extraction
    with tempfile.TemporaryDirectory() as temp_dir:
        # Extract JAR using our current logic
        target_dir = os.path.join(temp_dir, "extracted_jar")
        os.makedirs(target_dir, exist_ok=True)
        
        try:
            with zipfile.ZipFile(jar_path, 'r') as zip_ref:
                print(f"JAR contains {len(zip_ref.infolist())} entries")
                
                # List all entries in the JAR
                print("\n=== JAR Contents ===")
                for zip_info in zip_ref.infolist():
                    print(f"  {zip_info.filename} (size: {zip_info.file_size} bytes)")
                
                # Extract all files
                extracted_count = 0
                skipped_count = 0
                
                for zip_info in zip_ref.infolist():
                    try:
                        zip_name = zip_info.filename
                        
                        # Skip directory entries
                        if zip_name.endswith('/'):
                            skipped_count += 1
                            continue
                        
                        # Convert absolute paths to relative
                        if zip_name.startswith('/'):
                            zip_name = zip_name.lstrip('/')
                        
                        target_path = os.path.join(target_dir, zip_name)
                        os.makedirs(os.path.dirname(target_path), exist_ok=True)
                        
                        with zip_ref.open(zip_info) as source, open(target_path, 'wb') as target:
                            shutil.copyfileobj(source, target)
                        
                        extracted_count += 1
                        print(f"  ✓ Extracted: {zip_name}")
                        
                    except Exception as e:
                        print(f"  ✗ Failed to extract {zip_info.filename}: {e}")
                        continue
            
            print(f"\n=== Extraction Summary ===")
            print(f"  Extracted files: {extracted_count}")
            print(f"  Skipped directories: {skipped_count}")
            
            # Verify extraction results
            print(f"\n=== Extracted Files ===")
            extracted_files = []
            for root, dirs, files in os.walk(target_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, target_dir)
                    extracted_files.append(rel_path)
                    print(f"  {rel_path}")
            
            print(f"\nTotal extracted files: {len(extracted_files)}")
            
            # Check if extracted content matches JAR content
            with zipfile.ZipFile(jar_path, 'r') as zip_ref:
                jar_files = [info.filename for info in zip_ref.infolist() if not info.filename.endswith('/')]
            
            print(f"\n=== Content Comparison ===")
            print(f"JAR contains {len(jar_files)} non-directory files")
            print(f"Extracted {len(extracted_files)} files")
            
            # Find missing files
            missing_files = [f for f in jar_files if f.lstrip('/') not in extracted_files]
            if missing_files:
                print(f"\nWARNING: Missing files ({len(missing_files)}):")
                for f in missing_files[:10]:  # Show first 10
                    print(f"  {f}")
                if len(missing_files) > 10:
                    print(f"  ... and {len(missing_files) - 10} more")
            
            return True
            
        except Exception as e:
            print(f"ERROR during JAR extraction: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Main function"""
    # Test with a sample JAR file
    # You need to provide a path to an actual JAR file for testing
    test_jar = input("Enter path to JAR file for testing: ").strip()
    
    if not test_jar:
        print("No JAR file provided, exiting")
        return 1
    
    test_jar_extraction(test_jar)
    return 0

if __name__ == "__main__":
    main()
