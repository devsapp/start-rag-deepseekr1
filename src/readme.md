
> 注：当前项目为 Serverless Devs 应用，由于应用中会存在需要初始化才可运行的变量（例如应用部署地区、函数名等等），所以**不推荐**直接 Clone 本仓库到本地进行部署或直接复制 s.yaml 使用，**强烈推荐**通过 `s init ${模版名称}` 的方法或应用中心进行初始化，详情可参考[部署 & 体验](#部署--体验) 。

# cap-rag-deepseekr1 帮助文档

<description>

CAP rag with deeepseekr1

</description>


## 资源准备

使用该项目，您需要有开通以下服务并拥有对应权限：

<service>



| 服务/业务 |  权限  | 相关文档 |
| --- |  --- | --- |
| 函数计算 |  AliyunFCFullAccess | [帮助文档](https://help.aliyun.com/product/2508973.html) [计费文档](https://help.aliyun.com/document_detail/2512928.html) |
| 日志服务 |  AliyunFCServerlessDevsRolePolicy | [帮助文档](https://help.aliyun.com/zh/sls) [计费文档](https://help.aliyun.com/zh/sls/product-overview/billing) |
| 专有网络 |  AliyunFCServerlessDevsRolePolicy | [帮助文档](https://help.aliyun.com/zh/vpc) [计费文档](https://help.aliyun.com/zh/vpc/product-overview/billing) |
| 硬盘挂载 |  AliyunFCServerlessDevsRolePolicy | [帮助文档](https://help.aliyun.com/zh/nas) [计费文档](https://help.aliyun.com/zh/nas/product-overview/billing) |

</service>

<remark>



</remark>

<disclaimers>



</disclaimers>

## 部署 & 体验

<appcenter>
   
- :fire: 通过 [云原生应用开发平台 CAP](https://cap.console.aliyun.com/template-detail?template=cap-rag-deepseekr1) ，[![Deploy with Severless Devs](https://img.alicdn.com/imgextra/i1/O1CN01w5RFbX1v45s8TIXPz_!!6000000006118-55-tps-95-28.svg)](https://cap.console.aliyun.com/template-detail?template=cap-rag-deepseekr1) 该应用。
   
</appcenter>
<deploy>
    
   
</deploy>

## 案例介绍

<appdetail id="flushContent">

本文阐述如何构建一个检索增强生成（RAG）应用程序，该程序通过整合基于文件的知识库与云端托管的大语言模型实现，面向企业级应用场景，可应用于私有知识问答系统构建、客服自动化流程优化等场景。

</appdetail>




## 架构图

<framework id="flushContent">

![](https://img.alicdn.com/imgextra/i1/O1CN01TJKYqz1O7s78Ins1o_!!6000000001659-0-tps-1314-664.jpg)

</framework>

## 使用流程

<usedetail id="flushContent">

### 快速体验
部署成功后， 打开  rag_app 服务提供的域名， 您可以实现如下效果：

![](https://img.alicdn.com/imgextra/i4/O1CN019YM8C41s1OzXAgXSC_!!6000000005706-0-tps-2452-1686.jpg)

> 测试文件 [CAP_X50_Pro.docx](https://images.devsapp.cn/media/CAP_X50_Pro.docx)

RAG应用能够根据用户提供的文档生成回复，有效缓解大模型面对私有领域问题时的局限性，整体上可分为检索与生成两个环节。

在本应用中，检索环节在 rag_app  服务中执行，您能够便捷地管理和维护知识文档、灵活定义文档切分方法；embeding环节则调用由百炼提供的通义千问API，推理由托管的 DeepSeek-R1-Distill-Qwen-7B-GGUF 模型服务完成，您无需考虑本地计算资源及环境配置问题，即可获得比较优质的回复效果。 


### 传入知识文件
您可以通过以下两种方法之一向RAG应用传入知识文件：

> 若同时使用两种方法，RAG应用会优先参考临时性文件。

#### 传入临时性文件
如果您想要直接在对话框中上传文件，并基于该文件进行问答，可以在RAG问答页面单击输入框旁的image进行临时知识库文件的上传，便能直接输入问题并获得回复。该方法在页面刷新后无法找回上传的文件。

支持传入的文件类型有：pdf、docx、txt、xlsx、csv。


### 上传数据并创建知识库
如果您需要长期使用特定的知识库文件，建议您通过创建知识库的方法来传入知识文件。需要以下2步：

#### 上传数据

在**上传数据**页面，您可以上传非结构化数据（暂时支持pdf与docx）或结构化数据（xlsx或csv）。非结构化数据会上传到您命名的类目中，File/Unstructured中会新建一个您命名类目名称的文件夹，存放您上传的文件；结构化数据会上传到您命名的数据表中，File/Structured中会新建一个您命名数据表名称的文件夹，存放您上传的数据。

> 如果您需要删除类目或数据表，请在管理类目或管理数据表中操作。

#### 创建知识库

在**创建知识库**界面，您可以使用上一步创建的类目或数据表进行知识库的创建。您可以选择多个类目或多个数据表，并设置知识库名称，单击**确认创建知识库**，在界面上显示：知识库创建成功，可前往**RAG问答**进行提问后，即代表知识库创建完成。知识库文件会存放在VectorStore中您命名知识库名称的文件夹下。您可以前往**RAG问答**，在**加载知识库**位置选中创建的知识库，便可以输入问题进行问答。

> 如果您需要删除知识库，请在管理知识库中操作。

</usedetail>

## 二次开发指南

<development id="flushContent">

### 优化回复效果
您可以参考以下方法，来优化RAG应用的回复效果。

#### 修改模型参数与RAG参数

对于模型参数，您可以调整：

**温度参数**: 该参数用于控制模型生成的随机性，温度值越高生成的随机性越高。

**最大回复长度**: 该参数用于控制模型生成的最多token个数。如果您希望生成详细的描述可以将该值调高；如果希望生成简短的回答可以将该值调低。

**携带上下文轮数**: 该参数用于控制模型参考历史对话的轮数，设为1时表示模型在回复时不会参考历史对话信息。

对于RAG参数，您可以调整：

**召回片段数**: 该参数用于控制选择与用户输入最相关文本段的个数。该值越大，模型可获得的参考信息越多，但无用信息也可能增加；该值越小，模型可获得的参考信息越少，但无用信息可能减少。

**相似度阈值**: 该参数会剔除已被选择的相关文本段中，相似度低于该值的文本段。该值越大，模型可获得的参考信息越少，但无用信息可能减少。该值为0时，表示不对召回片段进行剔除。

#### 优化切分方法
RAG应用会对文档进行切分，不同文档有不同的最佳切分策略。在创建知识库的过程中，本应用针对结构化数据的切分进行了优化；对于非结构化数据，本应用采用了LlamaIndex默认的切分策略。您可以根据您的文档内容，进行定制化的切分。

#### 更换嵌入模型
嵌入模型对于检索过程十分重要，对于同一个知识文件，不同的嵌入模型可能有不同的表现。您可以尝试更换嵌入模型，查看召回的效果，以选出最符合您业务场景的嵌入模型。

#### 优化提示词
您可以在chat.py中找到prompt_template参数，并根据您的使用场景进行改写，使得大模型的回复更符合业务预期。

</development>






