'''
pip install openai
'''
import os
import json
from openai import OpenAI

class Llama3():
    # 可能的API配置
    API_CONFIGS = [
        # Llama 3.3
        {
            "base_url": "https://api.llama-api.com",
            "model_name": "llama3.3-70b"
        },
        # Llama 3.2
        {
            "base_url": "https://api.llama-api.com",
            "model_name": "llama3.2-3b"
        },
        {
            "base_url": "https://api.llama-api.com",
            "model_name": "llama3.2-1b"
        },
        # Llama 3.1
        {
            "base_url": "https://api.llama-api.com",
            "model_name": "llama3.1-70b"
        },
        {
            "base_url": "https://api.llama-api.com",
            "model_name": "llama3.1-8b"
        },
        # Llama 3
        {
            "base_url": "https://api.llama-api.com",
            "model_name": "llama3-70b"
        },
        {
            "base_url": "https://api.llama-api.com",
            "model_name": "llama3-8b"
        },
        # 备用 V1 API端点
        {
            "base_url": "https://api.llama-api.com/v1",
            "model_name": "llama3.2-3b"
        },
        {
            "base_url": "https://api.llama-api.com/v1",
            "model_name": "llama3-70b"
        }
    ]
    
    def __init__(self, model_path = None, api_key = None, proxy_url = "", prefix_prompt = '''请用少于25个字回答以下问题\n\n'''):
        self.history = []
        if proxy_url:
            os.environ['https_proxy'] = proxy_url if proxy_url else None
            os.environ['http_proxy'] = proxy_url if proxy_url else None
        
        if not api_key:
            print("警告：未提供API密钥，将使用默认测试密钥")
            api_key = 'LA-bcde398ac3ef443c961f2f0af94be707d8506d0995fa47d09d3fa907fd53298c'
        elif not api_key.startswith('LA-'):
            raise ValueError("无效的API密钥格式。Llama3 API密钥应该以'LA-'开头")
        
        # 尝试所有可能的API配置
        last_error = None
        successful_models = []
        
        print("\n🔄 开始测试可用的Llama模型...")
        
        for config in self.API_CONFIGS:
            try:
                print(f"\n尝试API配置: {config['base_url']} with model {config['model_name']}")
                self.client = OpenAI(
                    api_key=api_key,
                    base_url=config['base_url']
                )
                # 测试API连接
                response = self.client.chat.completions.create(
                    model=config['model_name'],
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=1
                )
                print(f"✅ 成功连接到Llama API，使用模型：{config['model_name']}")
                successful_models.append(config['model_name'])
                self.model_path = config['model_name']
                break
            except Exception as e:
                error_msg = str(e)
                if "Invalid model name" in error_msg:
                    print(f"❌ 模型名称无效: {config['model_name']}")
                elif "404" in error_msg:
                    print(f"❌ API端点不存在: {config['base_url']}")
                elif "401" in error_msg:
                    print(f"❌ API密钥无效或未授权")
                    break  # API密钥问题，停止尝试其他配置
                else:
                    print(f"❌ 配置失败: {error_msg}")
                last_error = e
                continue
        
        if last_error:
            print(f"\n❗ 所有API配置都失败了。请确保：")
            print("1. API密钥正确且有效")
            print("2. 网络连接正常")
            print("3. 代理设置正确（如果使用代理）")
            if successful_models:
                print(f"\n✅ 成功测试过的模型: {', '.join(successful_models)}")
            print(f"\n最后的错误: {last_error}")
            raise last_error
            
        self.prefix_prompt = prefix_prompt

    def generate(self, message, system_prompt="你是一个很有帮助的中文助手。"):
        try:
            # 添加用户消息到历史记录
            self.history += [{
                    "role": "user", 
                    "content": self.prefix_prompt + message if self.prefix_prompt else message
                }]
            
            # 构建消息列表
            messages = ([{"role": "system", "content": system_prompt}] if system_prompt else []) + self.history
            print(f"\nLlama3 API请求:\n模型: {self.model_path}\n消息: {json.dumps(messages, ensure_ascii=False, indent=2)}")
            
            # 发送API请求
            response = self.client.chat.completions.create(
                model=self.model_path,
                messages=messages,
                temperature=0.7,
                max_tokens=200
            )
            print(f"\nLlama3 API原始响应:\n{response}")
            
            # 处理响应
            if hasattr(response, 'choices') and len(response.choices) > 0:
                content = response.choices[0].message.content
            elif isinstance(response, dict) and 'choices' in response:
                content = response['choices'][0]['message']['content']
            elif isinstance(response, list) and len(response) > 0:
                # 处理列表类型的响应
                if isinstance(response[0], dict) and 'message' in response[0]:
                    content = response[0]['message']['content']
                elif isinstance(response[0], dict) and 'content' in response[0]:
                    content = response[0]['content']
                else:
                    raise ValueError(f"无法从响应中提取内容: {response}")
            else:
                raise ValueError(f"意外的API响应格式: {response}")
            
            # 添加助手回复到历史记录
            self.history += [{
                "role": "assistant",
                "content": content
            }]
            
            return content
            
        except Exception as e:
            print(f"\nLlama3 API错误: {str(e)}")
            return f"对不起，调用Llama3 API时出错: {str(e)}\n请检查API密钥和网络连接，然后重试。"

    def chat(self, system_prompt = "你是一个很有帮助的中文助手。", message = "", history=[]):
        response = self.generate(message, system_prompt)
        history.append((message, response))
        return response, history
        
    def clear_history(self):
        self.history = []
        
""" if __name__ == '__main__':
    API_KEY = 'LA-bcde398ac3ef443c961f2f0af94be707d8506d0995fa47d09d3fa907fd53298c'
    # 若使用ChatGPT，要保证自己的APIKEY可用，并且服务器可访问OPENAI
    llm = Llama3(api_key=API_KEY, proxy_url=None)
    answer = llm.generate("如何应对压力？")
    print(answer) """


def test():
    API_KEY = 'LA-bcde398ac3ef443c961f2f0af94be707d8506d0995fa47d09d3fa907fd53298c'
    # 若使用ChatGPT，要保证自己的APIKEY可用，并且服务器可访问OPENAI
    llm = Llama3(api_key=API_KEY, proxy_url=None)
    answer, history = llm.chat("", "你会说泰语么")
    print(answer, history)
    from time import sleep
    sleep(5)
    answer, history = llm.chat("", "用泰语介绍一下区块链")
    print(answer, history)


if __name__ == '__main__':
    test()