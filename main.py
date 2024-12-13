import os
import time
import threading
from enum import Enum

from dotenv import load_dotenv
from openai import OpenAI
from colorama import Fore, Style, init

# !: USAGE:
# Create a .env file with OPENAI_API_KEY=your-api-key
# > py main.py

# Initialize terminal colors
init(autoreset=True)

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class InputType(Enum):
    STRING = "string"
    INTEGER = "integer"


def loading_indicator(stop_event):
    spinner = ["|", "/", "-", "\\"]
    idx = 0
    print()  # Add newline before the spinner
    while not stop_event.is_set():
        print(Fore.YELLOW + f"\rLoading... {spinner[idx % len(spinner)]}", end="", flush=True)
        time.sleep(0.2)
        idx += 1
    print()  # Add newline after the spinner


def get_story_response(prompt, retries=3):
    """Fetches a story response from the OpenAI API based on the given prompt with retries."""
    stop_event = threading.Event()
    loading_thread = threading.Thread(target=loading_indicator, args=(stop_event,))
    loading_thread.start()

    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system",
                     "content": "You are a creative storyteller. Generate unique and engaging stories based on user input."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(Fore.RED + f"\nAttempt {attempt + 1}/{retries} failed: {str(e)}" + Fore.RESET)
            if attempt < retries - 1:
                print(Fore.YELLOW + "Retrying...\n" + Fore.RESET)
            else:
                return f"Error communicating with AI after {retries} attempts: {str(e)}"
        finally:
            stop_event.set()
            loading_thread.join()


def ask_user_input(prompt, input_type, valid_inputs=None):
    while True:
        user_input = input(Fore.BLUE + prompt + Fore.RESET).strip()

        if user_input.lower() == "exit":
            print(Fore.RED + "Exiting the program. Goodbye!" + Fore.RESET)
            exit()

        if input_type == InputType.STRING and user_input:
            if valid_inputs is None or user_input.lower() in valid_inputs:
                return user_input
            print(Fore.RED + "Invalid input. Please try again." + Fore.RESET)

        elif input_type == InputType.INTEGER:
            try:
                user_input = int(user_input)
                if valid_inputs is None or user_input in valid_inputs:
                    return user_input
                print(Fore.RED + "Invalid input. Please choose from the valid options." + Fore.RESET)
            except ValueError:
                print(Fore.RED + "Please enter a valid number." + Fore.RESET)

        else:
            print(Fore.RED + "Input cannot be empty. Please try again." + Fore.RESET)


def setup_character():
    """Sets up the character for the story and returns their details."""
    name = ask_user_input("What is your character's name? (Type 'exit' to quit): ", InputType.STRING)
    age = ask_user_input("How old is your character? (Type 'exit' to quit): ", InputType.INTEGER)
    profession = ask_user_input("What does your character do for a living? (Type 'exit' to quit): ", InputType.STRING)

    return name, age, profession


def short_story():
    """Generates a short story based on user input."""
    print(Fore.MAGENTA + "\n🎭 Welcome to your short story experience! 🎭\n" + Style.RESET_ALL)

    # Character setup
    name, age, profession = setup_character()

    print(Fore.GREEN + f"\nGreat! {name}, a {age}-year-old {profession}, is about to embark on an adventure...")

    # Chapter 1: Introduction
    prompt_intro = f"Write an introductory chapter about {name}, a {age}-year-old {profession}. Use dark humor and existential themes."
    intro = get_story_response(prompt_intro)
    print(Fore.GREEN + f"\n{intro}\n")

    # Chapter 2: User's Choice
    choice = ask_user_input(
        "Your character is faced with a choice:\n1. Explore the mysterious house\n2. Ignore it and move on\nChoose 1 or 2 (or type 'exit' to quit): ",
        InputType.STRING, valid_inputs=["1", "2"])
    if choice == "1":
        prompt_choice = f"{name} decides to explore the mysterious house. Write what happens next in a darkly comedic style."
    else:
        prompt_choice = f"{name} decides to ignore the mysterious house and walk away. Write what happens next in a darkly comedic style."
    chapter2 = get_story_response(prompt_choice)
    print(Fore.GREEN + f"\nChapter 2: The Choice\n{chapter2}\n")

    # Chapter 3: Another Choice
    choice = ask_user_input(
        "A new dilemma appears:\n1. Trust a stranger's advice\n2. Forge your own path\nChoose 1 or 2 (or type 'exit' to quit): ",
        InputType.STRING, valid_inputs=["1", "2"])
    if choice == "1":
        prompt_choice = f"{name} decides to trust a stranger's advice. Write what happens next in a darkly comedic style."
    else:
        prompt_choice = f"{name} decides to forge their own path. Write what happens next in a darkly comedic style."
    chapter3 = get_story_response(prompt_choice)
    print(Fore.GREEN + f"\nChapter 3: The Dilemma\n{chapter3}\n")

    # Chapter 4: Final Decision
    choice = ask_user_input(
        "The journey reaches its peak:\n1. Embrace the chaos\n2. Seek the truth\nChoose 1 or 2 (or type 'exit' to quit): ",
        InputType.STRING, valid_inputs=["1", "2"])
    if choice == "1":
        prompt_end = f"{name} chooses to embrace the chaos. Conclude their story in a dark and ironic tone."
    else:
        prompt_end = f"{name} seeks the truth. Conclude their story in a dark and ironic tone."
    ending = get_story_response(prompt_end)
    print(Fore.GREEN + f"\nChapter 4: The Conclusion\n{ending}\n")

    print(
        Fore.MAGENTA + "Thank you for playing! Remember, life is just a story, and we’re all characters in a cosmic joke.\n")


def ongoing_story():
    """Generates an ongoing story with choices at each iteration until the user stops."""
    print(Fore.MAGENTA + "\n🎭 Welcome to your ongoing story experience! 🎭\n" + Style.RESET_ALL)

    # Character setup
    name, age, profession = setup_character()

    print(
        Fore.GREEN + f"\nGreat! {name}, a {age}-year-old {profession}, is about to embark on an endless adventure...")

    while True:
        # Generate the next part of the story
        prompt = f"Continue the story of {name}, a {age}-year-old {profession}. Add a new twist, dilemma, or challenge in a darkly comedic style."
        story_part = get_story_response(prompt)
        print(Fore.GREEN + f"\nStory Update:\n{story_part}\n")

        # Provide the user with choices for the next part
        choice = ask_user_input(
            f"What should {name} do next?\n"
            "1. Take a bold and risky action\n"
            "2. Play it safe but risk missing an opportunity\n"
            "Choose 1 or 2 (or type 'exit' to quit): ",
            InputType.STRING,
            valid_inputs=["1", "2", "exit"]
        )

        # Add user choice to the story prompt
        if choice == "1":
            prompt = f"{name} takes a bold and risky action. Continue the story with a darkly comedic twist."
        elif choice == "2":
            prompt = f"{name} decides to play it safe but risks missing an opportunity. Continue the story with a darkly comedic twist."

        # Generate the next part of the story based on the choice
        story_part = get_story_response(prompt)
        print(Fore.GREEN + f"\nNext Chapter:\n{story_part}\n")

        # Ask if the user wants to continue
        continue_story = ask_user_input(
            "Would you like to continue the story? (yes or no): ",
            InputType.STRING,
            valid_inputs=["yes", "no", "y", "n", "exit"]
        )
        if continue_story.lower() in ["no", "n", "exit"]:
            print(Fore.RED + "Ending the story. Thanks for playing!" + Style.RESET_ALL)
            break


def main_menu():
    """Displays the main menu and handles user selection."""
    print(Fore.MAGENTA + "\n🎭 Welcome to Darkly Ever After! 🎭\n" + Style.RESET_ALL)

    while True:
        print(Fore.BLUE + "\n📜 Main Menu 📜")
        print(Fore.CYAN + "1. Short Story")
        print(Fore.CYAN + "2. Ongoing Story")
        print(Fore.CYAN + "0. Exit\n")

        choice = ask_user_input("Choose an option (1, 2, 0): ", InputType.INTEGER, valid_inputs=[1, 2, 0])

        if choice == 1:
            short_story()
        elif choice == 2:
            ongoing_story()
        elif choice == 0:
            print(Fore.RED + "Goodbye! Thank you for visiting the story generator.\n" + Style.RESET_ALL)
            break
        else:
            print(Fore.YELLOW + "Invalid choice. Please select 1, 2, or 0." + Style.RESET_ALL)


if __name__ == "__main__":
    main_menu()
