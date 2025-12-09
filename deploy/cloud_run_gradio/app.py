import os

import gradio as gr


def greet(name: str) -> str:
    """Return a friendly greeting."""
    cleaned = name.strip() or "there"
    return f"Hello, {cleaned}!"


demo = gr.Interface(
    fn=greet,
    inputs=gr.Textbox(label="Your name"),
    outputs=gr.Textbox(label="Greeting"),
    title="JarvisX Greeter",
    description="Simple example Gradio app containerised for Google Cloud Run.",
)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    demo.launch(
        server_name="0.0.0.0",
        server_port=port,
        show_api=False,
        inline=False,
        prevent_thread_lock=True,
    )

