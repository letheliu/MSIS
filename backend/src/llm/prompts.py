class PromptTemplates:
    SYSTEM_PROMPT = (
        "你是一个专业的军队公文写作助手。请根据提供的参考资料和格式要求，"
        "撰写符合军队公文写作规范的公文。要求用语规范、逻辑清晰、格式正确。"
    )

    GENERATION_TEMPLATE = """{system_prompt}

参考资料（由智能检索系统提供）：
{context}

公文类型：{doc_type}
主题：{topic}
字数要求：{word_count}字左右
风格：{style}

格式要求：
{format_requirements}

请严格按照{doc_type}的公文格式撰写，确保内容完整、用语规范。"""

    OPTIMIZATION_TEMPLATE = """请对以下公文内容进行优化，从以下几个方面给出具体修改建议：

1. 用语规范性：是否符合军队公文用语标准
2. 逻辑结构：论述是否清晰、层次是否分明
3. 格式合规性：是否符合公文格式规范
4. 内容完整性：是否有遗漏的关键要素

原文：
{content}

公文类型：{doc_type}

请逐条给出修改建议，并给出修改后的文本。"""

    TYPE_REQUIREMENTS = {
        "command": (
            "格式要求：\n"
            "1. 标题使用「关于XXX的命令」格式\n"
            "2. 正文以命令口吻撰写，用词果断、准确\n"
            "3. 包含受令单位、命令内容、执行要求、时限\n"
            "4. 署名为指挥机关全称"
        ),
        "notice": (
            "格式要求：\n"
            "1. 标题使用「关于XXX的通知」格式\n"
            "2. 正文包含：通知事由、具体要求、执行时限\n"
            "3. 语言正式、条理清晰\n"
            "4. 包含主送单位和落款"
        ),
        "report": (
            "格式要求：\n"
            "1. 标题使用「关于XXX的报告」格式\n"
            "2. 正文包含：情况概述、主要工作、成效分析、存在问题、下步打算\n"
            "3. 数据准确，论据充分\n"
            "4. 语言客观、实事求是"
        ),
        "summary": (
            "格式要求：\n"
            "1. 标题使用「XXX工作总结」格式\n"
            "2. 正文包含：基本情况、主要做法、取得成效、经验启示、下步计划\n"
            "3. 全面系统、重点突出\n"
            "4. 语言精炼、概括性强"
        ),
        "memo": (
            "格式要求：\n"
            "1. 标题使用「XXX会议纪要」格式\n"
            "2. 正文包含：会议时间地点、参会人员、议题、决议、责任分工\n"
            "3. 记录准确、要点清晰\n"
            "4. 突出决策事项和执行要求"
        ),
    }

    @classmethod
    def get_format_requirements(cls, doc_type: str) -> str:
        return cls.TYPE_REQUIREMENTS.get(doc_type, "")

    @classmethod
    def build_generation_prompt(
        cls,
        doc_type: str,
        topic: str,
        context: str,
        word_count: int = 800,
        style: str = "正式",
    ) -> str:
        format_req = cls.get_format_requirements(doc_type)
        return cls.GENERATION_TEMPLATE.format(
            system_prompt=cls.SYSTEM_PROMPT,
            context=context,
            doc_type=doc_type,
            topic=topic,
            word_count=word_count,
            style=style,
            format_requirements=format_req,
        )

    @classmethod
    def build_optimization_prompt(cls, content: str, doc_type: str) -> str:
        return cls.OPTIMIZATION_TEMPLATE.format(content=content, doc_type=doc_type)
