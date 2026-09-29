# file: out_msg_gui.py
import flet as ft
import gui_asyncio_client as gui_client

@ft.component
def Message_Creator():
    " create text fields for text entry and button to send_msg"
    receiver = ft.TextField(label="RECEIVER", width=120,  capitalization =ft.TextCapitalization.CHARACTERS)
    code = ft.TextField(label="CODE", width=80)
    arglist = ft.TextField( label="ARGLIST", width=250 )
    
    #create handler before adding the send button
    def send_msg(e):
        msg=  "{"+ f" SENDER : GUI, RECEIVER : {receiver.value} , CODE : {code.value} , ARGSLIST : [ {arglist.value} ]"+"}"
        print("msg: ", msg)
        gui_client.send(msg)

    send = ft.Button("Send",on_click = send_msg)
  
    return ft.Card(
        content=ft.Container(
        padding=10,
        content=ft.Row(
            controls=[
                receiver,
                code,
                arglist,
                send
                ]
            ),
        )
    )



@ft.component
def App():
    return ft.SafeArea(
        content=ft.Column(
            controls = [Message_Creator()]
            ),
        )

if __name__ == "__main__":
   ft.run(lambda page: page.render(App))
