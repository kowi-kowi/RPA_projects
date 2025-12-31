import subprocess
import os
from langdetect import detect
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM




def create_directory(path):
    """Tworzy katalog, jeśli nie istnieje."""
    try:
        os.makedirs(path, exist_ok=True)
        print(f"Katalog '{path}' został utworzony lub już istnieje.")
    except Exception as e:
        print(f"Błąd podczas tworzenia katalogu '{path}': {e}")
        return False
    return True

def remove_directory(path):
    """Usuwa katalog, jeśli istnieje."""
    try:
        os.rmdir(path)
        print(f"Katalog '{path}' został usunięty.")
    except Exception as e:
        print(f"Błąd podczas usuwania katalogu '{path}': {e}")
        return False
    return True 

def clone_repository(repo_url, clone_path):
    """Klonuje repozytorium GitHub do określonej ścieżki."""
    try:
        subprocess.run(['git', 'clone', repo_url, clone_path], check=True)
        print(f"Repozytorium '{repo_url}' zostało sklonowane do '{clone_path}'.")
    except subprocess.CalledProcessError as e:
        print(f"Błąd podczas klonowania repozytorium '{repo_url}': {e}")
        return False
    return True

def copy_file(src, dest):
    """Kopiuje plik z src do dest."""
    try:
        subprocess.run(['cp', src, dest], check=True)
        print(f"Plik '{src}' został skopiowany do '{dest}'.")
    except subprocess.CalledProcessError as e:
        print(f"Błąd podczas kopiowania pliku z '{src}' do '{dest}': {e}")
        return False
    return True

def list_files_in_directory(path):
    """Zwraca listę plików w podanym katalogu."""
    try:
        files = os.listdir(path)
        print(f"Pliki w katalogu '{path}': {files}")
        return files
    except Exception as e:
        print(f"Błąd podczas listowania plików w katalogu '{path}': {e}")
        return []
    
def remove_file(path):
    """Usuwa plik podanej ścieżki."""
    try:
        os.remove(path)
        print(f"Plik '{path}' został usunięty.")
    except Exception as e:
        print(f"Błąd podczas usuwania pliku '{path}': {e}")
        return False
    return True

def read_file(path):
    """Odczytuje zawartość pliku tekstowego."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except Exception as e:
        print(f"Błąd podczas odczytu pliku '{path}': {e}")
        return None

def save_file(path, content):
    """Zapisuje zawartość do pliku tekstowego."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Zawartość została zapisana do pliku '{path}'.")
    except Exception as e:
        print(f"Błąd podczas zapisywania do pliku '{path}': {e}")
        return False
    return True

def text_to_lines(text):
    """Dzieli tekst na linie."""
    return text.splitlines()

def detect_language(text):
    """Wykrywa język podanego tekstu."""
    try:
        language = detect(text)
        print(f"Wykryty język: {language}")
        return language
    except Exception as e:
        print(f"Błąd podczas wykrywania języka: {e}")
        return None

def split_file_into_chunks(path, chunk_size=10):
        """Dzieli plik tekstowy na mniejsze fragmenty o określonym rozmiarze (w liniach)."""
        os.makedirs("./Translate_Application/data/input", exist_ok=True)

        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        file_number = 1
        for i in range(0, len(lines), chunk_size):
            chunk_lines = lines[i:i + chunk_size]
            chunk_path = f"./Translate_Application/data/input/chunk_{file_number}.txt"
            with open(chunk_path, "w", encoding="utf-8") as chunk_file:
                chunk_file.writelines(chunk_lines)
            #print(f"Utworzono fragment: {chunk_path}")
            file_number += 1

        print(f"Utworzono plikow: {file_number - 1}")

def start_model(model_path):
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
    return tokenizer, model

def translate_text(text, tokenizer, model, source_language, target_language):
    """Tłumaczy podany tekst na docelowy język za pomocą zewnętrznego narzędzia tłumaczeniowego."""
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)

    forced_bos_token_id = tokenizer.convert_tokens_to_ids(target_language) #force model to use the code I need

    generated = model.generate(
        **inputs,
        forced_bos_token_id=forced_bos_token_id,
        max_length=128
    )

    return tokenizer.decode(generated[0], skip_special_tokens=True)

def to_unicode_escape(text):
    return text.encode('unicode_escape').decode('ascii')

