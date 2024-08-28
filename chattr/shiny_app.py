from subprocess import Popen, PIPE
from tempfile import NamedTemporaryFile
from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from json import loads
from os import path

if "_history_file" not in locals():
    _history_file = NamedTemporaryFile().name

if "_default_file" not in locals():
    _default_file = NamedTemporaryFile().name

if "_pkg_location" not in locals():
    _pkg_location = path.dirname(__file__)

btn_copy_no = 0

def app_add_user(x):
    ui.insert_ui(
        ui.layout_columns(
            ui.p(),
            ui.card(ui.markdown(x), style="background-color: #376CA4; color: white;"),
            col_widths=(1, 11),
        ),
        selector="#main",
        where="afterEnd",
    )


def app_add_assistant(x):
    ui.insert_ui(
        ui.layout_columns(
            ui.card(parse_response(x), style="padding:0; margin:0; border-color: #ccc;"),
            ui.p(),
            col_widths=(11, 1),
        ),
        selector="#main",
        where="afterEnd",
    )


app_ui = ui.page_fluid(
    ui.tags.style(".bslib-gap-spacing { padding:4px; font-size:90%; margin:1px; } "),
    ui.tags.style(".bslib-mb-spacing { padding:1px; margin:1px;}"),
    ui.tags.style(".bslib-grid-item { padding:1px; margin:1px;}"),
    ui.tags.style(".col-sm-11 { margin: 0px; padding-left: 2px; padding-right: 2px; }"),
    ui.tags.style(".col-sm-1 { margin: 0px; padding-left: 2px; padding-right: 2px; }"),
    #ui.tags.style(".container-fluid { display: grid; grid-template-rows: 1fr auto; }"),
    ui.panel_fixed(
        ui.row(
            ui.column(11,
                ui.input_text_area("prompt", "", width="100%", resize=False)
            ),
            ui.column(1,
            ui.div(
                ui.input_task_button(
                    "submit", "Submit", style="font-size:65%; padding:4px; margin:2px"
                ),
                ui.div(
                    ui.input_dark_mode(id="mode"),
                )            
            )
        )), width="98%;"), 
    ui.panel_absolute(
        ui.layout_columns(ui.output_ui("value"), ui.p(), col_widths=(11, 1)),
        ui.output_ui(id="main"), 
        top = "60px", 
        width= "98%"
        ),
)

def parse_response(x):
    global btn_copy_no
    x_split = x.split("```")
    out = ""
    ret = ()
    is_code = False
    ignore_rw = False
    for i in x_split:
        out = out + i
        if is_code:
            if i == "":
                ignore_rw = True
            else:
                ignore_rw = False
            btn_copy_no = btn_copy_no + 1
            btn_id = "copy" + str(btn_copy_no)
            i = "```" + i + "```"
            rw =  ui.div(
                ui.row(
                    ui.column(11), 
                    ui.column(
                        1, ui.input_task_button(btn_id, "Copy", style="font-size:65%; padding:4px; margin:2px")
                        )                    
                ), 
                ui.row(ui.markdown(i))
            ) 
        else:
            ignore_rw = False
            rw =  ui.row(
                ui.markdown(i)                
            )            
        if is_code == False:
            is_code = True
        else:
            is_code = False

        if i != "``````":
            ret = ret, rw
    return(ret)

def server(input: Inputs, output: Outputs, session: Session):
    response = ""
    proc = ""

    if path.isfile(_history_file):
        history = loads(open(_history_file, "r").read())
        for entries in history:
            role = entries.get("role")
            content = entries.get("content")
            if role == "user":
                app_add_user(content)
            if role == "assistant":
                app_add_assistant(content)

    @reactive.effect
    @reactive.event(input.submit)
    def _():
        nonlocal proc
        if input.prompt() != "":
            script_path = path.join(_pkg_location, "cli.py")
            args = [
                "python",
                script_path,
                f"--prompt={input.prompt()}",
                f"--history={_history_file}",
                f"--default={_default_file}",
            ]
            proc = Popen(args, stdout=PIPE)
            ui.update_text("prompt", value="")
            app_add_user(input.prompt())

    @render.text
    def value():
        nonlocal response
        nonlocal proc
        out = ""
        reactive.invalidate_later(0.1)
        if hasattr(proc, "stdout"):
            out = proc.stdout.read(3)
            if out:
                out = str(out.decode())
                response = response + out
            else:
                if response != "":
                    app_add_assistant(response)
                    response = ""
        return ui.markdown(response)


app = App(app_ui, server)
