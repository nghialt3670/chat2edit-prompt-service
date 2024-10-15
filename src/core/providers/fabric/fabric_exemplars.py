from typing import Dict, List

from core.controller.execute import DEFAULT_FEEDBACK
from models.phase import ChatPhase, Execution, Message, PromptPhase
from schemas.language import Language


def create_fabric_exemplars() -> Dict[Language, List[ChatPhase]]:
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
                    answers=[
                        (
                            "THINKING: We need find the dog first before we can remove it.\n"
                            "COMMANDS:\n"
                            'dogs = await segment_image_objects_by_prompt(image0, prompt="dog")'
                        )
                    ],
                    execution=Execution(
                        commands=[
                            'dogs = await segment_image_objects_by_prompt(image0, prompt="dog")'
                        ],
                        feedback=Message(
                            src="system",
                            type="warning",
                            text="Segmented 2 `dog` in `image0`.",
                            varnames=["annotated_image0"],
                        ),
                    ),
                ),
                PromptPhase(
                    answers=[
                        (
                            "THINKING: There are 2 dogs in the image so we need to show the annotated image and ask the user to specify which one to be removed.\n"
                            "COMMANDS:\n"
                            'await response_to_user(text="Trong ảnh có 2 con chó, bạn muốn chọn con nào để xóa?", attachments=[annotated_image0])'
                        )
                    ],
                    execution=Execution(
                        commands=[
                            'await response_to_user(text="Trong ảnh có 2 con chó, bạn muốn chọn con nào để xóa?", attachments=[annotated_image0])'
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
                    answers=[
                        (
                            "THINKING: We need to find the house first before we can increase the brightness of it.\n"
                            "COMMANDS:\n"
                            'houses = await segment_image_objects_by_prompt(image0, prompt="house")'
                        )
                    ],
                    execution=Execution(
                        commands=[
                            'houses = await segment_image_objects_by_prompt(image0, prompt="house")'
                        ],
                        feedback=Message(
                            src="system",
                            type="info",
                            text="Segmented 0 `house` in `image0`.",
                        ),
                    ),
                ),
                PromptPhase(
                    answers=[
                        (
                            "THINKING: Since the function cannot find a house in the image, we inform the user and suggest alternative methods to locate the house (such as using a box, for example).\n"
                            "COMMANDS:\n"
                            'await response_to_user(text="Chúng tôi không thể tìm thấy ngôi nhà trong hình ảnh. Vui lòng thử các phương pháp khác để xác định vị trí ngôi nhà, chẳng hạn như sử dụng khung để khoanh vùng.")'
                        )
                    ],
                    execution=Execution(
                        commands=[
                            'await response_to_user(text="Chúng tôi không thể tìm thấy ngôi nhà trong hình ảnh. Vui lòng thử các phương pháp khác để xác định vị trí ngôi nhà, chẳng hạn như sử dụng khung để khoanh vùng.")',
                        ],
                        response=Message(
                            src="llm",
                            type="response",
                            text="Chúng tôi không thể tìm thấy ngôi nhà trong hình ảnh. Vui lòng thử các phương pháp khác để xác định vị trí ngôi nhà, chẳng hạn như sử dụng khung để khoanh vùng.",
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
                    answers=[
                        (
                            "THINKING: The user provided a box so we should use segment_image_objects_by_boxes function to segment the object and return it to the user.\n"
                            "COMMANDS:\n"
                            "obj = (await segment_image_objects_by_boxes(image0, boxes=[box0]))[0]\n"
                            'await response_to_user(text="Đây là vật thể đã được cắt ra từ khung.", attachments=[obj])'
                        )
                    ],
                    execution=Execution(
                        commands=[
                            "obj = (await segment_image_objects_by_boxes(image0, boxes=[box0]))[0]",
                            'await response_to_user(text="Đây là vật thể đã được cắt ra từ khung.", attachments=[obj])',
                        ],
                        feedback=DEFAULT_FEEDBACK,
                        response=Message(
                            src="llm",
                            type="response",
                            text="Đây là vật thể đã được cắt ra từ khung.",
                            varnames=["obj"],
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
                text="Please remove the dog from the picture",
                varnames=["image0"],
            ),
            prompt_phases=[
                PromptPhase(
                    answers=[
                        (
                            "THINKING: We need to find the dog first before we can remove it.\n"
                            "COMMANDS:\n"
                            'dogs = await segment_image_objects_by_prompt(image0, prompt="dog")'
                        )
                    ],
                    execution=Execution(
                        commands=[
                            'dogs = await segment_image_objects_by_prompt(image0, prompt="dog")'
                        ],
                        feedback=Message(
                            src="system",
                            type="warning",
                            text="Segmented 2 `dogs` in `image0`.",
                            varnames=["annotated_image0"],
                        ),
                    ),
                ),
                PromptPhase(
                    answers=[
                        (
                            "THINKING: There are 2 dogs in the image, so we need to show the annotated image and ask the user to specify which one to remove.\n"
                            "COMMANDS:\n"
                            'await response_to_user(text="There are 2 dogs in the image, which one would you like to remove?", attachments=[annotated_image0])'
                        )
                    ],
                    execution=Execution(
                        commands=[
                            'await response_to_user(text="There are 2 dogs in the image, which one would you like to remove?", attachments=[annotated_image0])'
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
                text="Increase the brightness of the house by around 15%",
                varnames=["image0"],
            ),
            prompt_phases=[
                PromptPhase(
                    answers=[
                        (
                            "THINKING: We need to find the house first before we can increase its brightness.\n"
                            "COMMANDS:\n"
                            'houses = await segment_image_objects_by_prompt(image0, prompt="house")'
                        )
                    ],
                    execution=Execution(
                        commands=[
                            'houses = await segment_image_objects_by_prompt(image0, prompt="house")'
                        ],
                        feedback=Message(
                            src="system",
                            type="info",
                            text="Segmented 0 `house` in `image0`.",
                        ),
                    ),
                ),
                PromptPhase(
                    answers=[
                        (
                            "THINKING: Since the function cannot find a house in the image, we inform the user and suggest alternative methods to locate the house (such as using a box, for example).\n"
                            "COMMANDS:\n"
                            'await response_to_user(text="We couldn’t find the house in the image. Please try alternative methods to identify the house, such as using a box to mark the area.")'
                        )
                    ],
                    execution=Execution(
                        commands=[
                            'await response_to_user(text="We couldn’t find the house in the image. Please try alternative methods to identify the house, such as using a box to mark the area.")',
                        ],
                        response=Message(
                            src="llm",
                            type="response",
                            text="We couldn’t find the house in the image. Please try alternative methods to identify the house, such as using a box to mark the area.",
                        ),
                    ),
                ),
            ],
        ),
        ChatPhase(
            request=Message(
                src="user",
                type="request",
                text="Crop the object within the box for me",
                varnames=["image0", "box0"],
            ),
            prompt_phases=[
                PromptPhase(
                    answers=[
                        (
                            "THINKING: The user provided a box, so we should use the segment_image_objects_by_boxes function to segment the object and return it to the user.\n"
                            "COMMANDS:\n"
                            "obj = (await segment_image_objects_by_boxes(image0, boxes=[box0]))[0]\n"
                            'await response_to_user(text="Here is the object cropped from the box.", attachments=[obj])'
                        )
                    ],
                    execution=Execution(
                        commands=[
                            "obj = (await segment_image_objects_by_boxes(image0, boxes=[box0]))[0]",
                            'await response_to_user(text="Here is the object cropped from the box.", attachments=[obj])',
                        ],
                        feedback=DEFAULT_FEEDBACK,
                        response=Message(
                            src="llm",
                            type="response",
                            text="Here is the object cropped from the box.",
                            varnames=["obj"],
                        ),
                    ),
                ),
            ],
        ),
    ]

    return {"vi": FABRIC_VI_EXEMPLARS, "en": FABRIC_EN_EXEMPLARS}
