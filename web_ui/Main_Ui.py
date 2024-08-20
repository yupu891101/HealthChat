from web_ui.Chat_Bot import ChatBot
from web_ui.Tab1 import Tab1
from web_ui.Tab2 import Tab2
import gradio as gr
import os

os.environ["CUDA_VISIBLE_DEVICES"] = "0"

def main():
    tab1 = Tab1()
    tab2 = Tab2()
    chatbox = ChatBot(tab1=tab1)

    with gr.Blocks(theme='Tshackelton/IBMPlex-DenseReadable', title="HealthChat") as healthchat:
        gr.Markdown("""
            <style>
                .recording {
                    background-color: red !important;
                    color: white !important;
                }
            </style>
            <div style='text-align: center;'>
                <h1 style='margin-bottom: 0.5rem;'>HealthChat: A Conversational AI Solution</h1>
            </div>
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                with gr.Row():
                    # model = gr.Dropdown(label="Choose Model", value="module_v7", choices=["module_v7", "llama3"])
                    gender = gr.Dropdown(label="Chatbot gender", value="male", choices=["male", "female"])
                
                # tab1
                with gr.Tab(label="Choose Voice"):
                    with gr.Row():
                        refresh_button = gr.Button("Refresh")
                    with gr.Row():
                        input_pt = gr.FileExplorer(label="Voice's checkpoint", root="./DDSP-SVC/exp", glob="**/*.pt*", file_count="single")
                    with gr.Row():
                        with gr.Column():
                            keychange = gr.Slider(label="Pitch", minimum=-20, maximum=20, step=1, value=0)
                            speedup = gr.Slider(label="Speedup", minimum=-10, maximum=10, step=1, value=1)
                    with gr.Row():
                        run_button = gr.Button("Start converting sounds")
                    with gr.Row():
                        run_output = gr.Text(label="Conversion result")
                    with gr.Row():
                        output_audio = gr.Audio(label="New Chatbot Voice")

                    refresh_button.click(
                        fn=tab1.refresh_tab1,
                        outputs=[input_pt, keychange, speedup]
                    )
                    run_button.click(
                        tab1.change_voice,
                        inputs=[input_pt, keychange, speedup, gender],
                        outputs=[run_output, output_audio]
                    )
                    
                # tab2
                with gr.Tab("Clone Voice"):
                    with gr.Row():
                        gr.Markdown("Each wav file takes more than 2 seconds, and it is recommended to upload 20 files.")
                    with gr.Row():
                        input_wav = gr.File(label="Upload .wav file to train", file_count="multiple")
                    with gr.Row():
                        with gr.Column():
                            dir_path = gr.Text(label="Your voice's name")
                        with gr.Column():
                            epoch = gr.Number(label="Epoch", value=5000, interactive=True)
                    with gr.Row():
                        learn_button = gr.Button("Learn your voice")
                        stop_button = gr.Button("Stop learning")
                    with gr.Row():
                        run_output = gr.Text(label="Learning result")

                    learn_button.click(
                        tab2.learn_voice,
                        inputs=[input_wav, dir_path, epoch],
                        outputs=run_output
                    )
                    stop_button.click(tab2.stop_training)
                
            # chatbot
            with gr.Column(scale=3):
                with gr.Row(equal_height=True):
                    with gr.Column():
                        chatbot = gr.Chatbot(
                            [],
                            elem_id="chatbot",
                            bubble_full_width=False,
                            height=750,
                        )
                        msg = gr.MultimodalTextbox(interactive=True, file_types=["image"], placeholder="Enter message or upload file...", show_label=False)
                with gr.Row():
                    restart = gr.Button(value="🔁  Restart Chat")
                    audio_btn = gr.Button(value="🔴  Speak")
                with gr.Row():
                    wo = gr.WaveformOptions(sample_rate=16000)
                    audio_box = gr.Audio(label="Record", sources="microphone", type="numpy", format="wav", waveform_options=wo, visible=False)
                    output_audio = gr.Audio(label="Generated Audio", type='filepath', autoplay=True, visible=False)
                
                chatbot.like(chatbox.print_like_dislike, None, None)
                restart.click(
                    fn=chatbox.clear_history,
                    inputs=None,
                    outputs=[chatbot, msg, output_audio]
                )
                
                # Input with text
                chat_msg = msg.submit(chatbox.add_message, inputs=[msg], outputs=[chatbot, msg])
                bot_msg = chat_msg.then(chatbox.bot_response, inputs=[chatbot, input_pt, keychange, speedup, gender], outputs=[chatbot, output_audio])
                bot_msg.then(lambda: gr.MultimodalTextbox(interactive=True), None, [msg])

                # Input with button
                audio_btn.click(
                    fn=chatbox.action, 
                    inputs=[audio_btn, audio_box], 
                    outputs=[audio_btn, audio_box]
                ).\
                then(fn=lambda: None, js=ChatBot.click_js()).\
                then(fn=chatbox.check_btn, inputs=audio_btn)
                
                trans_msg = audio_box.stop_recording(chatbox.transcribe, inputs=[audio_box], outputs=[chatbot])
                trans_msg.then(
                    chatbox.bot_response, 
                    inputs=[chatbot, input_pt, keychange, speedup, gender], 
                    outputs=[chatbot, output_audio]
                )

    healthchat.queue().launch(share=True)

if __name__ == "__main__":
    main()
