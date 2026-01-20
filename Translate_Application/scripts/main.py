############ Algorithm to translate text from one language to another ############
# 1. Get the input text from github repository
# 2. Detect the source language of the text
# 3. Divide the text into manageable chunks
# 4. Translate the chunks to the target language
# 5. Check for output language correctness
# 6. Combine the translated chunks into a single text
# 7. Save the translated text back to the github repository


import tools
import os

def main():

    input_file_path = "./Translate_Application/data/messages.properties"
    translated_output_dir = "./Translate_Application/data/translated_output"
    source_language = "eng_Latn"  # Przykładowy język źródłowy
    target_language = "nld_Latn"  # Przykładowy język docelowy


    # 1. Get the input text from github repository
    #tools.clone_repository(repo_url, clone_path)

    # 2. Detect the source language of the text
    #source_language = tools.detect_language(input_file_path)

    # 3. Divide the text into manageable chunks
    #tools.split_file_into_chunks(input_file_path)

    # 4. Translate the chunks to the target language

    tokenizer, model = tools.start_model("facebook/nllb-200-distilled-600M")

    list_of_files = os.listdir("./Translate_Application/data/input")
    for file_name in list_of_files:
        filename = file_name
        translated_lines = []
        file_path = os.path.join("./Translate_Application/data/input", file_name)
        text = tools.read_file(file_path)
        if text:
            lines = tools.text_to_lines(text)
            for line in lines:
                line = line.strip()
                if '=' in line:
                    prefix, text_to_translate = line.split('=', 1)
                    translated_line = tools.translate_text(text_to_translate, tokenizer, model, source_language, target_language)
                    reconstructed_line = f"{prefix}={translated_line}"
                    translated_lines.append(reconstructed_line)
                else:
                    pass
                translated_text = translated_text + "\n" + tools.translate_text(line, tokenizer, model, source_language, target_language)

        output_filepath = os.path.join(translated_output_dir, filename)
        with open(output_filepath, "w") as f_out:
            for translated_line in translated_lines:
                f_out.write(translated_line + '\n') # Add newline back for each line
        
        tools.remove_file(file_path)

                


    # 5. Check for output language correctness
    # (Implement your own logic here)

    # 6. Combine the translated chunks into a single text
    # (Implement your own logic here)

    # 7. Save the translated text back to the github repository
    # (Implement your own logic here)
if __name__ == "__main__":
    main()
