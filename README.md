# Global AI Week – AI Hackathon (Organized by upstage) 
Navigating Business Establishment Laws and Civic Laws in Japan and Korea is challenging due to language barriers and the intricate nature of legal terminology across different jurisdictions. Foreign entrepreneurs and businesses find it particularly difficult to understand and comply with local Business Establishment Laws, hindering their ability to operate smoothly in Japan and Korea. In the legal domain, navigating and understanding complex laws, especially in multiple languages, poses significant challenges. This is particularly evident in the context of Business Establishment Laws and Civic Laws in Japan and Korea.  

## To address these challenges, we developed an AI-driven solution using Solaris Document AI, Solaris LLM and Predibase:
Created 6 domain-specific datasets
- Fine-tune 6 LoRA adapters for enhanced legal understanding.
- Implement a classification system for automatic adapter selection.
- Develop a web application hosted on Huggingface Space to demonstrate this AI-powered legal advisor.

## Results: 
LoRA Adapters showed excellent performance for Korean and Japanese legal contexts, moderate performance for English legal contexts, and poor performance for unsupported languages like Bengali. Also, LoRA adapter was very good at classification, which we used for automatic adapter selection.   Overall, each adapter improves legal understanding, and factual accuracy.



## Proposed Methodology  
![image](https://github.com/user-attachments/assets/bab04e3d-b2eb-485f-910c-2c419d9e7ef3) 


## Generated Dataset Details
![image](https://github.com/user-attachments/assets/342ef0d2-138c-40c7-8de1-9bc361669050)


## Finetuned for Adapter Classification
Number of Class: 4
```
Sample Input: How does a company usually pay insurance premiums in Japan?

Adapter Output: 
“Japanese business law”  
``` 
Using this output, we can select the appropriate finetuned adapter to answer this domain specific question.  

![image](https://github.com/user-attachments/assets/70881ca0-855c-498e-8ae5-9ca8311b9d62)


