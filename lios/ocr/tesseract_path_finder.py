import os
import shutil
import subprocess
import glob

class TesseractPathFinder:
    """Comprehensive tesseract tessdata path discovery utility"""
    
    @staticmethod
    def find_paths(verbose=False):
        """
        Find all tessdata directory paths on the system.
        
        Args:
            verbose (bool): If True, prints search progress
        
        Returns:
            list: List of tessdata directory paths, empty if none found
        """
        paths = []
        
        if verbose:
            print("Searching for tessdata paths...")
        
        # 1. Environment variable
        env_path = os.environ.get('TESSDATA_PREFIX')
        if env_path and os.path.isdir(env_path) and TesseractPathFinder._is_valid_tessdata_dir(env_path):
            paths.append(env_path)
            if verbose:
                print(f"Found via ENV: {env_path}")
        
        # 2. From all tesseract binary locations
        tess_binaries = TesseractPathFinder._find_tesseract_binaries()
        for tess_bin in tess_binaries:
            bin_dir = os.path.dirname(os.path.realpath(tess_bin))
            
            relative_paths = [
                "../share/tesseract-ocr/tessdata",
                "../share/tesseract/tessdata", 
                "../../share/tesseract-ocr/tessdata",
                "../../share/tesseract/tessdata",
                "../tessdata",
                "tessdata"
            ]
            
            for rel in relative_paths:
                path = os.path.normpath(os.path.join(bin_dir, rel))
                if os.path.isdir(path) and TesseractPathFinder._is_valid_tessdata_dir(path) and path not in paths:
                    paths.append(path)
                    if verbose:
                        print(f"Found via binary: {path}")
        
        # 3. Direct from tesseract
        tessdata_from_binary = TesseractPathFinder._get_tessdata_from_tesseract()
        for path in tessdata_from_binary:
            if path not in paths:
                paths.append(path)
                if verbose:
                    print(f"Found via tesseract: {path}")
        
        # 4. Comprehensive filesystem search
        if verbose:
            print("Performing filesystem search...")
        
        found_paths = TesseractPathFinder._comprehensive_tessdata_search()
        for path in found_paths:
            if path not in paths:
                paths.append(path)
                if verbose:
                    print(f"Found via search: {path}")
        
        # 5. User-specific locations
        user_paths = TesseractPathFinder._check_user_locations()
        for path in user_paths:
            if path not in paths:
                paths.append(path)
                if verbose:
                    print(f"Found in user dir: {path}")
        
        if verbose:
            print(f"Total found: {len(paths)} tessdata paths")
        
        return paths

    @staticmethod
    def find_primary_path(verbose=False):
        """
        Get the primary (first/best) tessdata directory path.
        
        Args:
            verbose (bool): If True, prints search progress
            
        Returns:
            str: Primary tessdata path, None if not found
        """
        paths = TesseractPathFinder.find_paths(verbose=verbose)
        return paths[0] if paths else None

    @staticmethod
    def find_valid_paths():
        """
        Find tessdata paths that contain valid configuration files.
        
        Returns:
            list: List of valid tessdata directory paths
        """
        paths = TesseractPathFinder.find_paths()
        valid_paths = []
        
        for path in paths:
            if os.path.exists(path):
                # Check for box.train config file or just accept if tessdata exists
                if os.path.isfile(path + "/configs/box.train") or TesseractPathFinder._is_valid_tessdata_dir(path):
                    valid_paths.append(path)
        
        return valid_paths

    @staticmethod
    def get_languages_from_path(dirpath):
        """
        Get available languages from a specific tessdata directory.
        
        Args:
            dirpath (str): Path to tessdata directory
            
        Returns:
            list: List of available language codes
        """
        langs = []
        if os.access(dirpath, os.R_OK):
            try:
                for filename in os.listdir(dirpath):
                    if filename.lower().endswith('.traineddata'):
                        lang = filename[:-12]  # Remove '.traineddata'
                        langs.append(lang)
            except (OSError, PermissionError):
                pass
        return langs

    @staticmethod
    def get_all_languages():
        """
        Get all available languages from all found tessdata paths.
        
        Returns:
            list: Sorted list of unique language codes
        """
        langs = []
        tessdata_paths = TesseractPathFinder.find_paths()
        
        for dirpath in tessdata_paths:
            if os.path.isfile(dirpath + "/configs/box.train"):
                for item in TesseractPathFinder.get_languages_from_path(dirpath):
                    if item not in langs:  # Avoid duplicates
                        langs.append(item)
        
        # If no languages found with box.train, try without this requirement
        if not langs:
            for dirpath in tessdata_paths:
                for item in TesseractPathFinder.get_languages_from_path(dirpath):
                    if item not in langs:
                        langs.append(item)
        
        return sorted(langs)

    # Private helper methods
    @staticmethod
    def _find_tesseract_binaries():
        """Find all tesseract binary locations"""
        binaries = []
        
        # Method 1: which command
        tess_bin = shutil.which("tesseract")
        if tess_bin:
            binaries.append(tess_bin)
        
        # Method 2: Common locations
        common_paths = [
            "/usr/bin/tesseract",
            "/usr/local/bin/tesseract", 
            "/opt/tesseract/bin/tesseract",
            "/bin/tesseract"
        ]
        
        for path in common_paths:
            if os.path.isfile(path) and os.access(path, os.X_OK) and path not in binaries:
                binaries.append(path)
        
        # Method 3: Search filesystem
        search_dirs = ["/usr", "/opt", "/usr/local"]
        for search_dir in search_dirs:
            if os.path.exists(search_dir):
                try:
                    found = TesseractPathFinder._search_for_binaries(search_dir, "tesseract")
                    for binary in found:
                        if binary not in binaries:
                            binaries.append(binary)
                except (PermissionError, OSError):
                    continue
        
        return binaries

    @staticmethod
    def _search_for_binaries(root_dir, binary_name, max_depth=3):
        """Search for binary files"""
        found = []
        
        def _search(current_dir, depth):
            if depth > max_depth:
                return
            
            try:
                for entry in os.listdir(current_dir):
                    entry_path = os.path.join(current_dir, entry)
                    
                    if os.path.isfile(entry_path) and entry == binary_name:
                        if os.access(entry_path, os.X_OK):
                            found.append(entry_path)
                    elif os.path.isdir(entry_path) and not os.path.islink(entry_path):
                        if any(bin_dir in entry for bin_dir in ['bin', 'sbin']):
                            _search(entry_path, depth + 1)
            except (PermissionError, OSError):
                pass
        
        _search(root_dir, 0)
        return found

    @staticmethod
    def _get_tessdata_from_tesseract():
        """Get tessdata paths from tesseract binary"""
        paths = []
        binaries = TesseractPathFinder._find_tesseract_binaries()
        
        for binary in binaries:
            try:
                result = subprocess.run([binary, "--print-parameters"], 
                                      capture_output=True, text=True, timeout=5)
                for line in result.stdout.split('\n'):
                    if 'tessdata' in line.lower():
                        parts = line.split()
                        for part in parts:
                            if 'tessdata' in part and os.path.isdir(part) and TesseractPathFinder._is_valid_tessdata_dir(part):
                                paths.append(part)
            except:
                continue
        
        return list(set(paths))

    @staticmethod
    def _comprehensive_tessdata_search():
        """Search filesystem for tessdata directories"""
        found_paths = []
        search_roots = ["/usr", "/usr/local", "/opt", "/var"]
        
        for root in search_roots:
            if os.path.exists(root):
                try:
                    paths = TesseractPathFinder._search_tessdata_recursive(root, max_depth=5)
                    found_paths.extend(paths)
                    
                    # Glob patterns for efficiency
                    patterns = [f"{root}/**/tessdata", f"{root}/share/**/tessdata"]
                    for pattern in patterns:
                        try:
                            matches = glob.glob(pattern, recursive=True)
                            for match in matches:
                                if os.path.isdir(match) and TesseractPathFinder._is_valid_tessdata_dir(match):
                                    found_paths.append(match)
                        except:
                            continue
                except:
                    continue
        
        return list(set(found_paths))

    @staticmethod
    def _search_tessdata_recursive(root_dir, max_depth=5):
        """Recursive search for tessdata"""
        found = []
        
        def _search(current_dir, depth):
            if depth > max_depth:
                return
            
            try:
                if os.path.basename(current_dir) == 'tessdata':
                    if TesseractPathFinder._is_valid_tessdata_dir(current_dir):
                        found.append(current_dir)
                
                for entry in os.listdir(current_dir):
                    entry_path = os.path.join(current_dir, entry)
                    if os.path.isdir(entry_path) and not os.path.islink(entry_path):
                        skip_dirs = {'proc', 'sys', 'dev', 'run', 'tmp'}
                        if entry not in skip_dirs:
                            _search(entry_path, depth + 1)
            except:
                pass
        
        _search(root_dir, 0)
        return found

    @staticmethod
    def _check_user_locations():
        """Check user-specific tessdata locations"""
        paths = []
        home = os.path.expanduser("~")
        
        locations = [
            f"{home}/.local/share/tesseract/tessdata",
            f"{home}/.tesseract/tessdata",
            f"{home}/tesseract/tessdata"
        ]
        
        for location in locations:
            if os.path.isdir(location) and TesseractPathFinder._is_valid_tessdata_dir(location):
                paths.append(location)
        
        return paths

    @staticmethod
    def _is_valid_tessdata_dir(path):
        """Check if directory contains tessdata files"""
        try:
            files = os.listdir(path)
            return any(f.endswith('.traineddata') for f in files)
        except:
            return False


# Convenience functions for backward compatibility
def find_tessdata_paths(verbose=False):
    """Find all tessdata paths - convenience function"""
    return TesseractPathFinder.find_paths(verbose=verbose)

def find_primary_tessdata_path(verbose=False):
    """Find primary tessdata path - convenience function"""
    return TesseractPathFinder.find_primary_path(verbose=verbose)


# Example usage and testing
if __name__ == "__main__":
    print("=== Tesseract Path Finder Demo ===")
    
    # Find all paths
    print("\n1. All tessdata paths:")
    all_paths = TesseractPathFinder.find_paths(verbose=True)
    for i, path in enumerate(all_paths, 1):
        print(f"   {i}. {path}")
    
    # Primary path
    print(f"\n2. Primary tessdata path: {TesseractPathFinder.find_primary_path()}")
    
    # Valid paths
    print(f"\n3. Valid tessdata paths: {TesseractPathFinder.find_valid_paths()}")
    
    # Available languages
    print(f"\n4. Available languages: {TesseractPathFinder.get_all_languages()}")
