import requests
import json

class ComplaintClassifier:
    def __init__(self, base_url="http://localhost:11434/api/generate", model="llama3.2"):
        self.base_url = base_url
        self.model = model

    def classify_complaint(self, text: str) -> str:
        """
        Sends complaint text to local Ollama model and extracts clean response.
        """
        prompt = f"""
        Classify this citizen complaint into one of the following categories:
        [neighbor, noise, dogs, cars, city_services, robbery, assault, utilities (internet, electricity, water, phone)]
        Complaint: {text}
        Reply with only the category name.
        """

        response = requests.post(self.base_url, json={"model": self.model, "prompt": prompt}, stream=True)
        
        if response.status_code == 200:
            result_text = ""
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode("utf-8"))
                        if "response" in data:
                            result_text += data["response"]
                    except json.JSONDecodeError:
                        continue

          
            result_text = result_text.strip().lower()

            print("Model raw output:", result_text)

           
            valid_categories = [
                "neighbor", "noise", "dogs", "cars", "city_services",
                "robbery", "assault", "utilities", "internet", "electricity", "water", "phone"
            ]

            for cat in valid_categories:
                if cat in result_text:
                    return cat

            return "unknown"

        print(" Ollama request failed:", response.status_code, response.text)
        return "unknown"
