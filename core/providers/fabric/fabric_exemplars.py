from chat2edit.models.chat_cycle import ChatCycle
from chat2edit.models.chat_message import ChatMessage
from chat2edit.models.exec_message import ExecMessage
from chat2edit.models.prompt_cycle import PromptCycle

FABRIC_EXEMPLARS = [
    [
        ChatCycle(
            req_message=ChatMessage(
                sender="user", text="Hãy xóa con mèo đi", attachment_varnames=["image0"]
            ),
            prompt_cycles=[
                PromptCycle(
                    thinking="We need to detect the cat first.",
                    exec_message=ExecMessage(
                        status="warning",
                        text="Detected 2 'cat' in the image",
                        executed_commands=['cats = detect(image_0, "cat")'],
                        attachment_varnames=["annotated_image_0"],
                    ),
                ),
                PromptCycle(
                    thinking="There are 2 detected cats in the image, we need to ask user to specify which one.",
                    exec_message=ExecMessage(
                        status="warning",
                        text="Detected 2 'cat' in the image",
                        executed_commands=[
                            'response_user(text="Trong ảnh có 2 con mèo, bạn muốn xóa con nào?", images=[annotated_image_0])'
                        ],
                        attachment_varnames=["annotated_image_0"],
                    ),
                ),
            ],
            res_message=ChatMessage(
                sender="system",
                text="Trong ảnh có 2 con mèo, bạn muốn xóa con nào?",
                attachment_varnames=["annotated_image_0"],
            ),
        ),
    ],
    [
        ChatCycle(
            req_message=ChatMessage(
                sender="user",
                text="Hãy tăng độ sáng của bức ảnh",
                attachment_varnames=["image_0"],
            ),
            prompt_cycles=[
                PromptCycle(
                    thinking="We need to ask user how much brightness they want to increase.",
                    exec_message=ExecMessage(
                        status="info",
                        text="Commands executed successfully.",
                        executed_commands=[
                            'response_user(text="Bạn muốn tăng độ sáng bao nhiêu?")'
                        ],
                    ),
                )
            ],
            res_message=ChatMessage(
                sender="system",
                text="Bạn muốn tăng độ sáng lên bao nhiêu?",
            ),
        ),
        ChatCycle(
            req_message=ChatMessage(sender="user", text="Khoảng 20%"),
            prompt_cycles=[
                PromptCycle(
                    thinking="We have all the information we need, let's edit the image.",
                    exec_message=ExecMessage(
                        status="info",
                        text="Commands executed successfully.",
                        executed_commands=[
                            "image_0 = apply_filter(image_0, 'brightness', 1.2)",
                            'response_user(text="Đây là ảnh sau khi đã tăng độ sáng 20%", images=[image_0])',
                        ],
                    ),
                )
            ],
            res_message=ChatMessage(
                sender="system",
                text="Đây là ảnh sau khi được tăng độ sáng 20%",
                attachment_varnames=["image_0"],
            ),
        ),
    ],
]
