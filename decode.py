import string


def decode_text_and_numbers(text):
    result = []
    length = len(text)
    
    for i, char in enumerate(text):
        if char in string.ascii_letters:  # Process letters
            shift = i + 1  # Position-based shift
            if length % 2 == 0:
                new_char = chr(ord(char) + shift) if i % 2 == 0 else chr(ord(char) - shift)
            else:
                new_char = chr(ord(char) - shift) if i % 2 == 0 else chr(ord(char) + shift)
            
            if char.isupper():
                new_char = chr((ord(new_char) - 65) % 26 + 65)
            elif char.islower():
                new_char = chr((ord(new_char) - 97) % 26 + 97)
            
            result.append(new_char)
        elif char.isdigit():  # Process numbers
            shift = i + 1
            num = int(char)
            
            if length % 2 == 0:
                new_num = (num + shift) % 10 if i % 2 == 0 else (num - shift) % 10
            else:
                new_num = (num - shift) % 10 if i % 2 == 0 else (num + shift) % 10
            
            result.append(str(new_num))
        else:  # Keep special characters and spaces unchanged
            result.append(char)
    
    return "".join(result)

# text = input("Enter the text to decode: ")

# decoded_text = decode_text_and_numbers(text)
# print("Decoded:", decoded_text)
# input()