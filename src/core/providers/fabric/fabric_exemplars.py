from core.controller.execute import DEFAULT_FEEDBACK
from models.phase import ChatPhase, Execution, Message, PromptPhase


def create_fabric_exemplars():

    FABRIC_VI_EXEMPLARS = [
        ChatPhase(
            request=Message(
                src="user",
                type="request",
                text="Hãy xóa con chó khỏi bức ảnh",
                varnames=["image0"],
            ),
            prompt_phases=[
                PromptPhase(
                    responses=[
                        'THINKING: We need detect the dog first before we can remove it.\nCOMMANDS:\ndogs = detect(image0, prompt="dog")'
                    ],
                    execution=Execution(
                        commands=['dogs = detect(image0, prompt="dog")'],
                        feedback=Message(
                            src="system",
                            type="warning",
                            text="Detected 2 `dog` in `image0`",
                            varnames=["annotated_image0"],
                        ),
                    ),
                ),
                PromptPhase(
                    responses=[
                        'THINKING: There are 2 dogs in the image so we need to show the annotated image and ask the user to specify which one to be removed.\nCOMMANDS:\nresponse_user(text="Trong ảnh có 2 con chó, bạn muốn chọn con nào để xóa?", attachments=[annotated_image0])'
                    ],
                    execution=Execution(
                        commands=[
                            'response_user(text="Trong ảnh có 2 con chó, bạn muốn chọn con nào để xóa?", attachments=[annotated_image0])'
                        ],
                        response=Message(
                            src="llm",
                            type="response",
                            text="Trong ảnh có 2 con chó, bạn muốn chọn con nào để xóa?",
                            varnames=["annotated_image0"],
                        ),
                    ),
                ),
            ],
        ),
        ChatPhase(
            request=Message(
                src="user",
                type="request",
                text="Hãy tăng độ sáng của ngôi nhà lên khoảng 15%",
                varnames=["image0"],
            ),
            prompt_phases=[
                PromptPhase(
                    responses=[
                        'THINKING: We need to detect the house first before we can increase the brightness of it.\nCOMMANDS:\nhouses = detect(image0, prompt="house")'
                    ],
                    execution=Execution(
                        commands=['houses = detect(image0, prompt="house")'],
                        feedback=Message(
                            src="system",
                            type="info",
                            text="Detected 1 `house` in `image0`",
                        ),
                    ),
                ),
                PromptPhase(
                    responses=[
                        'THINKING: We detected the house, now we can do the next step.\nCOMMANDS:\nimage1 = filter(image0, filter_name="brightness", filter_value=1.15, targets=houses)\nresponse_user(text="Đây là bức ảnh sau khi đã tăng độ sáng ngôi nhà lên 15%.", attachments=[image1])'
                    ],
                    execution=Execution(
                        commands=[
                            'image1 = filter(image0, filter_name="brightness", filter_value=1.15, targets=houses)',
                            'response_user(text="Đây là bức ảnh sau khi đã tăng độ sáng ngôi nhà lên 15%.", attachments=[image1])',
                        ],
                        response=Message(
                            src="llm",
                            type="response",
                            text="Đây là bức ảnh sau khi đã tăng độ sáng ngôi nhà lên 15%.",
                            varnames=["image1"],
                        ),
                    ),
                ),
            ],
        ),
        ChatPhase(
            request=Message(
                src="user",
                type="request",
                text="Cắt cho tôi vật thể trong khung",
                varnames=["image0", "box0"],
            ),
            prompt_phases=[
                PromptPhase(
                    responses=[
                        "THINKING: The user provided a box so we should use segment function to segment the object and return it to the user.\nCOMMANDS:\nobject = segment(image0, box=box0)"
                    ],
                    execution=Execution(
                        commands=["object = segment(image0, box=box0)"],
                        feedback=DEFAULT_FEEDBACK,
                    ),
                ),
                PromptPhase(
                    responses=[
                        'THINKING: The object has been successfully segmented and returned.\nCOMMANDS:\nresponse_user(text="Đây là vật thể đã được cắt ra từ khung.", attachments=[object])'
                    ],
                    execution=Execution(
                        commands=[
                            'response_user(text="Đây là vật thể đã được cắt ra từ khung.", attachments=[object])'
                        ],
                        response=Message(
                            src="llm",
                            type="response",
                            text="Đây là vật thể đã được cắt ra từ khung.",
                            varnames=["object"],
                        ),
                    ),
                ),
            ],
        ),
    ]

    FABRIC_EN_EXEMPLARS = [
        ChatPhase(
            request=Message(
                src="user",
                type="request",
                text="Please remove the dog from the photo",
                varnames=["image0"],
            ),
            prompt_phases=[
                PromptPhase(
                    responses=[
                        'THINKING: We need to detect the dog first before we can remove it.\nCOMMANDS:\ndogs = detect(image0, prompt="dog")'
                    ],
                    execution=Execution(
                        commands=['dogs = detect(image0, prompt="dog")'],
                        feedback=Message(
                            src="system",
                            type="warning",
                            text="Detected 2 `dogs` in `image0`",
                            varnames=["annotated_image0"],
                        ),
                    ),
                ),
                PromptPhase(
                    responses=[
                        'THINKING: There are 2 dogs in the image, so we need to show the annotated image and ask the user to specify which one to remove.\nCOMMANDS:\nresponse_user(text="There are 2 dogs in the image, which one would you like to remove?", attachments=[annotated_image])'
                    ],
                    execution=Execution(
                        commands=[
                            'response_user(text="There are 2 dogs in the image, which one would you like to remove?", attachments=[annotated_image])'
                        ],
                        response=Message(
                            src="llm",
                            type="response",
                            text="There are 2 dogs in the image, which one would you like to remove?",
                            varnames=["annotated_image0"],
                        ),
                    ),
                ),
            ],
        ),
        ChatPhase(
            request=Message(
                src="user",
                type="request",
                text="Please increase the brightness of the house by about 15%",
                varnames=["image0"],
            ),
            prompt_phases=[
                PromptPhase(
                    responses=[
                        'THINKING: We need to detect the house first before we can increase its brightness.\nCOMMANDS:\nhouses = detect(image0, prompt="house")'
                    ],
                    execution=Execution(
                        commands=['houses = detect(image0, prompt="house")'],
                        feedback=Message(
                            src="system",
                            type="info",
                            text="Detected 1 `house` in `image0`",
                        ),
                    ),
                ),
                PromptPhase(
                    responses=[
                        'THINKING: We detected the house, now we can proceed to the next step.\nCOMMANDS:\nimage1 = filter(image0, filter_name="brightness", filter_value=1.15, targets=houses)\nresponse_user(text="Here is the image after increasing the brightness of the house by 15%.", attachments=[image1])'
                    ],
                    execution=Execution(
                        commands=[
                            'image1 = filter(image0, filter_name="brightness", filter_value=1.15, targets=houses)',
                            'response_user(text="Here is the image after increasing the brightness of the house by 15%.", attachments=[image1])',
                        ],
                        response=Message(
                            src="llm",
                            type="response",
                            text="Here is the image after increasing the brightness of the house by 15%.",
                            varnames=["image1"],
                        ),
                    ),
                ),
            ],
        ),
        ChatPhase(
            request=Message(
                src="user",
                type="request",
                text="Please crop the object in the box",
                varnames=["image0", "box0"],
            ),
            prompt_phases=[
                PromptPhase(
                    responses=[
                        "THINKING: The user provided a box, so we should use the segment function to isolate the object and return it to the user.\nCOMMANDS:\nobject = segment(image0, box=box0)"
                    ],
                    execution=Execution(
                        commands=["object = segment(image0, box=box0)"],
                        feedback=DEFAULT_FEEDBACK,
                    ),
                ),
                PromptPhase(
                    responses=[
                        'THINKING: The object has been successfully cropped and returned.\nCOMMANDS:\nresponse_user(text="Here is the object cropped from the box.", attachments=[object])'
                    ],
                    execution=Execution(
                        commands=[
                            'response_user(text="Here is the object cropped from the box.", attachments=[object])'
                        ],
                        response=Message(
                            src="llm",
                            type="response",
                            text="Here is the object cropped from the box.",
                            varnames=["object"],
                        ),
                    ),
                ),
            ],
        ),
    ]

    return FABRIC_VI_EXEMPLARS, FABRIC_EN_EXEMPLARS
