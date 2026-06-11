import os
import sys
import re
import struct
from io import BytesIO
from PIL import Image, ImageFile

# Force Pillow to load and attempt recovery of broken/truncated ransomware files
ImageFile.LOAD_TRUNCATED_IMAGES = True

MODEL_DIR = "__models__"
g_models = []

# REGEX CONFIGURATION: Matches '.JPG.' followed by any trailing ransomware extension
g_reg_exp = re.compile(r"\.JPG\.[^.]+$", re.IGNORECASE)


class TModel:
    def __init__(self, name: str, header: bytes, sos_bloc: bytes):
        self.name = name          
        self.header = header      
        self.sos_bloc = sos_bloc  

    def append_file_data(self, file_data: bytes) -> Image.Image:
        if len(file_data) >= 2 and file_data[0] == 0xFF and file_data[1] == 0xDA:
            data = self.header + file_data
        else:
            data = self.header + self.sos_bloc + file_data
        
        # Open and allow processing despite data stream issues
        return Image.open(BytesIO(data))


def main():
    load_models()
    
    args = sys.argv[1:]
    if not args:
        print("Usage: python script.py <path_to_corrupted_file1> ...")
        return

    for file_path in args:
        print(f"\n{'-'*72}\nFile: {os.path.basename(file_path)}")

        if first_options(file_path):
            print(">>>> Done!\n")
            continue

        file_data = load_file(file_path)

        for model in g_models:
            print(f">> Model: {model.name}")

            try:
                img = model.append_file_data(file_data)
            except Exception as e:
                print(f">>>> Error: {e}\n")
                continue

            cleaned_base = g_reg_exp.sub("", file_path)
            base_new_name = f"{cleaned_base}-{model.name}"
            
            try:
                img.save(base_new_name, "JPEG", quality=98)
                print(f">>>> Done: {os.path.basename(base_new_name)}")
            except Exception as e:
                print(f">>>> Error: {e}")
            
            print()

    input(f"{'-'*72}\nPress enter to exit...")


def first_options(file_path: str) -> bool:
    try:
        with open(file_path, "rb") as f:
            data = f.read()
    except Exception:
        return False

    # UPDATED: Strip the exact 153605 encrypted bytes
    data = data[153605:]
    data = data[:-36] if len(data) > 36 else b""

    id_sos = data.rfind(b"\xFF\xDA")
    if id_sos != -1:
        last_id = -1
        for i in range(id_sos - 1, -1, -1):
            if i + 1 < len(data) and data[i] == 0xFF and data[i+1] in (0xDB, 0xC0, 0xC4):
                last_id = i
            if i + 1 < len(data) and data[i] == 0xFF and data[i+1] not in (0xDB, 0xC0, 0xC4):
                break

        if last_id != -1:
            print(">> Option 01: Found 0xFFDA (SOS) preceded by some valid essential markers")
            
            buff_data = b"\xFF\xD8" + data[last_id:]
            
            try:
                img = Image.open(BytesIO(buff_data))
                img.load()  
            except Exception:
                return False

            cleaned_base = g_reg_exp.sub("", file_path)
            new_file = f"{cleaned_base}-option_FFDA.jpg"
            print(f">>>> {os.path.basename(new_file)} validated")
            
            try:
                with open(new_file, "wb") as hf:
                    hf.write(buff_data)
                return True
            except Exception as e:
                print(f">>>> Error: {e}\n")
                return False
                
    return False


def load_file(file_path: str) -> bytes:
    try:
        with open(file_path, "rb") as f:
            data = f.read()
    except Exception as e:
        print(f"Fatal error reading file: {e}")
        sys.exit(1)

    id_marker = data.rfind(b"\xFF\xDA")
    
    # UPDATED: Check marker boundaries relative to the new 153605 offset
    if id_marker == -1 or id_marker < 153605:
        print(">> No SOS (0xFFDA) marker found. First 153605 bytes will be stripped.")
        try:
            padding_str = input(">> How much padding do you want in the beginning of the stream? ")
            padding = int(padding_str) if padding_str.strip() else 0
        except ValueError:
            padding = 0

        data = data[153605:]
        if padding > 0:
            data = b"\x00" * padding + data
    else:
        data = data[id_marker:]
        
    return data


def load_models():
    try:
        self_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    except Exception as e:
        print(f"Fatal error getting script directory: {e}")
        sys.exit(1)

    models_path = os.path.join(self_dir, MODEL_DIR)
    
    if os.path.exists(models_path):
        for root, dirs, files in os.walk(models_path):
            for file in files:
                full_path = os.path.join(root, file)
                try:
                    model = model_load(full_path)
                    g_models.append(model)
                except Exception as e:
                    print(f"Model load error for file '{file}': {e}")

    if not g_models:
        raise RuntimeError(
            f"No models found!\nCreate a folder called \"{MODEL_DIR}\" next to this script "
            "and fill it with unencrypted pictures taken with the same camera configuration..."
        )


def model_load(file_path: str) -> TModel:
    with open(file_path, "rb") as f:
        data = f.read()

    id_marker = data.rfind(b"\xFF\xDA")
    if id_marker == -1:
        raise ValueError(f"Model {os.path.basename(file_path)} is invalid JPEG (no SOS 0xFFDA marker)")

    name = os.path.basename(file_path)
    header = data[:id_marker]

    sz = struct.unpack(">H", data[id_marker+2 : id_marker+4])[0]
    sos_bloc = data[id_marker : id_marker + 2 + sz]

    return TModel(name, header, sos_bloc)


if __name__ == "__main__":
    main()
