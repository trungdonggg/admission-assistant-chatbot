from classifier.utils import *
from classifier.cls_template import *


class Classifier:
    def __init__(self):
        self.model = get_model()

    async def ainvoke(self, prompt_components: ClassifierTemplate):
        prompt = await get_classifier_prompt().ainvoke(prompt_components.model_dump())
        print(prompt)
        return await self.model.ainvoke(prompt)
    


