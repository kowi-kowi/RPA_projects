############ Algorithm to translate text from one language to another ############
# 1. Get the input text from github repository
# 2. Detect the source language of the text
# 3. Divide the text into manageable chunks
# 4. Translate the chunks to the target language
# 5. Check for output language correctness
# 6. Combine the translated chunks into a single text
# 7. Save the translated text back to the github repository

import os
from github import Github
from langdetect import detect
