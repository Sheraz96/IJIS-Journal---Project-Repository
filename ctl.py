import anthropic
import os
import re

def load_prompt_from_file(filepath):
    """
    Load the system prompt from a text file.
    
    Args:
        filepath (str): D:\Claude CTL Generator\ctl_prompt.txt
    
    Returns:
        str: The prompt content
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        raise FileNotFoundError(f"Prompt file not found: {filepath}")
    except Exception as e:
        raise Exception(f"Error reading prompt file: {str(e)}")

def load_api_key(key_file='api_key.txt'):
    """
    Load API key from file, environment variable, or return None.
    Priority: 1) File, 2) Environment variable
    
    Args:
        key_file (str):D:\Claude CTL Generator\api_key.txt

    Returns:
        str: API key or None
    """

    if os.path.exists(key_file):
            try:
                with open(key_file, 'r', encoding='utf-8') as f:
                    api_key = f.read().strip()
                    if api_key:
                        return api_key
            except Exception as e:
                print(f"️  Warning: Could not read API key from {key_file}: {str(e)}")
        
    return os.environ.get("ANTHROPIC_API_KEY")

def extract_ctl_formula(response_text):
    """Extract the CTL formula from the LLM response."""
    patterns = [
        r'CTL translation is:\s*([^.\n]+)\.?FINISH',
        r'CTL formula:\s*([^.\n]+)',
        r'translation is:\s*([^.\n]+)\.?FINISH',
        r'final CTL translation is:\s*([^.\n]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, response_text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    lines = response_text.strip().split('\n')
    for line in reversed(lines):
        if any(op in line for op in ['EF', 'AF', 'EG', 'AG', 'EX', 'AX', 'EU', 'AU']):
            return line.strip().rstrip('.')
    
    return "CTL formula not found in expected format"

def generate_ctl_specification(natural_language_input, api_key=None, prompt_file=None, system_prompt=None):
    """
    Generate CTL specification from natural language input.
    
    Args:
        natural_language_input (str): The natural language sentence to translate
        api_key (str, optional): Anthropic API key. If None, reads from ANTHROPIC_API_KEY env var
        prompt_file (str, optional): Path to a text file containing the system prompt
        system_prompt (str, optional): Direct system prompt string
    
    Returns:
        dict: Contains 'ctl_formula' and 'full_explanation'
    """
    
    if api_key is None:
        api_key = load_api_key()
    
    if not api_key:
        raise ValueError(
            "API key not found. Please provide it as an argument or set ANTHROPIC_API_KEY environment variable.\n"
            "Get your API key from: https://console.anthropic.com/"
        )
    
    client = anthropic.Anthropic(api_key=api_key)
    
    if system_prompt is None:
        if prompt_file is None:
            raise ValueError(
                "No prompt provided. Please either:\n"
                "  1. Provide prompt_file parameter pointing to a .txt file\n"
                "  2. Provide system_prompt parameter as a string\n"
                "  3. Create a 'ctl_prompt.txt' file in the same directory"
            )
        system_prompt = load_prompt_from_file(prompt_file)
    
    user_message = f"{system_prompt}\n\nNatural Language: {natural_language_input}"
    
    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )
        
        full_response = message.content[0].text
        
        ctl_formula = extract_ctl_formula(full_response)
        
        return {
            "ctl_formula": ctl_formula,
            "full_explanation": full_response,
            "success": True
        }
    
    except Exception as e:
        return {
            "ctl_formula": None,
            "full_explanation": None,
            "success": False,
            "error": str(e)
        }

def batch_process_from_file(input_file, output_file=None, api_key=None, prompt_file=None):
    """
    Process multiple natural language sentences from a file.
    
    Args:
        input_file (str): Path to file with natural language sentences (one per line)
        output_file (str, optional): Path to save results. If None, prints to console
        api_key (str, optional): Anthropic API key
        prompt_file (str, optional): Path to prompt file
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            sentences = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"❌ Input file not found: {input_file}")
        return
    
    results = []
    
    for i, sentence in enumerate(sentences, 1):
        print(f"\n[{i}/{len(sentences)}] Processing: {sentence}")
        result = generate_ctl_specification(sentence, api_key=api_key, prompt_file=prompt_file)
        
        if result["success"]:
            results.append({
                "input": sentence,
                "ctl_formula": result["ctl_formula"],
                "explanation": result["full_explanation"]
            })
            print(f"✓ CTL: {result['ctl_formula']}")
        else:
            results.append({
                "input": sentence,
                "error": result["error"]
            })
            print(f"✗ Error: {result['error']}")
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            for r in results:
                f.write(f"Input: {r['input']}\n")
                if 'ctl_formula' in r:
                    f.write(f"CTL Formula: {r['ctl_formula']}\n")
                    f.write(f"Explanation:\n{r['explanation']}\n")
                else:
                    f.write(f"Error: {r['error']}\n")
                f.write("-" * 80 + "\n\n")
        print(f"\n✓ Results saved to: {output_file}")
    else:
        print("\n" + "=" * 80)
        print("BATCH RESULTS")
        print("=" * 80)
        for r in results:
            print(f"\nInput: {r['input']}")
            if 'ctl_formula' in r:
                print(f"CTL: {r['ctl_formula']}")
            else:
                print(f"Error: {r['error']}")

def main():
    """Main function for interactive CLI usage."""
    print("=" * 60)
    print("CTL Specification Generator".center(60))
    print("=" * 60)
    print("\nCTL Operators Reference:")
    print("  A  - For all paths")
    print("  E  - There exists a path")
    print("  G  - Always/Globally")
    print("  F  - Finally/Eventually")
    print("  X  - Next state")
    print("  U  - Until")
    print("\n" + "=" * 60 + "\n")
    
    api_key = load_api_key()    
    if not api_key:
        print("ANTHROPIC_API_KEY not found in environment variables.")
        print("Please set it before running this script:")
        print("  export ANTHROPIC_API_KEY='your-api-key-here'")
        print("\nOr get your API key from: https://console.anthropic.com/")
        return
    
    else:
        print("API key loaded successfully")
    
    prompt_file = "ctl_prompt.txt"
    if not os.path.exists(prompt_file):
        print(f"Required prompt file not found: {prompt_file}")
        print(f"\nPlease create '{prompt_file}' with your CTL prompt template.")
        print("Example content:")
        print("-" * 60)
        print("You are a Computational Tree Logic (CTL) expert...")
        print("-" * 60)
        return
    
    print(f"✓ Using prompt from: {prompt_file}\n")
    
    print("Options:")
    print("  1. Interactive mode (enter sentences one by one)")
    print("  2. Batch mode (process from file)")
    choice = input("\nSelect mode (1 or 2): ").strip()
    
    if choice == "2":
        input_file = input("Enter input file path: ").strip()
        output_file = input("Enter output file path (or press Enter to print): ").strip()
        output_file = output_file if output_file else None
        batch_process_from_file(input_file, output_file, api_key=api_key, prompt_file=prompt_file)
        return
    
    while True:
        print("\nEnter natural language sentence (or 'quit'):")
        user_input = input("> ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye!")
            break
        
        if not user_input:
            print("Please enter a valid sentence.")
            continue
        
        print("\n⏳ Generating CTL specification...\n")
        
        result = generate_ctl_specification(user_input, api_key=api_key, prompt_file=prompt_file)
        
        if result["success"]:
            print("=" * 60)
            print("CTL FORMULA:")
            print("=" * 60)
            print(f"  {result['ctl_formula']}")
            print("=" * 60)
            print("\nFULL EXPLANATION:")
            print("-" * 60)
            print(result['full_explanation'])
            print("=" * 60)
        else:
            print(f" Error: {result['error']}")

if __name__ == "__main__":
    main()