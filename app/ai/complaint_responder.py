import requests
import json

class ComplaintResponder:
    def __init__(self, base_url="http://localhost:11434/api/generate", model="llama3.2"):
        self.base_url = base_url
        self.model = model

    def generate_reply(self, citizen_name: str, complaint_text: str, complaint_type: str) -> str:
        """
        توليد رد بشري طبيعي من نموذج Llama بناءً على نوع الشكوى ونصها.
        """
        prompt = f"""
        أنت موظف خدمة عملاء محترم في بلدية المدينة الذكية.
        المواطن اسمه {citizen_name}.
        نوع الشكوى: {complaint_type}.
        نص الشكوى: "{complaint_text}"

        المطلوب منك: اكتب ردًا بشريًا لبقًا ومهذبًا يشعر المواطن بالاهتمام،
        ويؤكد له أن البلدية استلمت شكواه، وتوضح الخطوة القادمة باختصار.
        لا تستخدم لغة آلية، بل لغة طبيعية قريبة من الإنسان.
        لا تتكلم كثيرا وقل المعلومه بشكل مناسب 
        """

        response = requests.post(self.base_url, json={"model": self.model, "prompt": prompt}, stream=True)
        if response.status_code == 200:
            reply_text = ""
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode("utf-8"))
                        if "response" in data:
                            reply_text += data["response"]
                    except json.JSONDecodeError:
                        continue

            return reply_text.strip()

        print(" Llama reply failed:", response.status_code, response.text)
        return "شكرًا لتواصلك معنا، تم استلام الشكوى وسيتم متابعتها قريبًا."
