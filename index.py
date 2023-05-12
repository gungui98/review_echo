import argparse
import re

from flask import send_from_directory
from views import screen_0
from views import screen_1
from views import screen_2
from views.screen_1 import *

server = app.server

PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"
ROOT_DICOM_MP4 = os.environ["ROOT_DICOM_MP4"]

NAVBAR = dbc.Navbar(
    children=[
        html.A(
            dbc.Row(
                [
                    dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px")),
                    dbc.Col(
                        dbc.NavbarBrand("Dicom Reviews", className="ml-2")
                    ),
                ],
                align="center",
                no_gutters=True,
            ),
            href="/"
        )
    ],
    color="dark",
    dark=True,
    sticky="top",
)

BODY = html.Div(
    [
        dcc.Location(id='url', refresh=False),
        # dcc.Interval(
        #     id='interval-component',
        #     interval=3 * 1000,  # in milliseconds
        #     n_intervals=0
        # ),
        html.Div(id='page-content')

    ],
    className="eleven columns body",
)


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return screen_0.layout
    if re.fullmatch(r'\/case_id=.+[0-9a-zA-Z]', pathname):
        case_id = pathname.replace('/case_id=', '')
        return screen_1.get_layout(case_id)
    if re.fullmatch(r'\/dicom_id=.+[0-9a-zA-Z]', pathname):

        id = pathname.replace('/dicom_id=', '')
        id = id.replace('&case_id=', ',')
        dicom_id, case_id = id.split(',')
        return screen_2.get_layout(case_id, dicom_id)
    else:
        return '404'


@server.route("/data/<path:path>")
def download(path):
    """Serve a file from the upload directory."""
    return send_from_directory('data', path, as_attachment=True)


@server.route("/screen_1/images/<directory>/<filename>")
def load_thumbnail_screen_1(directory, filename):
    """Serve a file from the upload directory."""
    path = os.path.join(ROOT_DICOM_MP4, directory, filename)
    if not os.path.exists(path):
        return send_from_directory('./data', 'image-not-found-scaled.png', as_attachment=True)
    return send_from_directory(os.path.join(ROOT_DICOM_MP4, directory), filename, as_attachment=True)


@server.route("/screen_2/video/<directory>/<filename>")
def load_video(directory, filename):
    """Serve a file from the upload directory."""
    path = os.path.join(ROOT_DICOM_MP4, directory, filename)
    if not os.path.exists(path):
        return send_from_directory('./data', 'sample_video.mp4', as_attachment=True)
    return send_from_directory(os.path.join(ROOT_DICOM_MP4, directory), filename, as_attachment=True)


app.layout = html.Div(children=[NAVBAR, BODY])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='program argument')
    parser.add_argument('--mode', type=str, default='production',
                        help='path to json file')
    args = parser.parse_args()
    if args.mode == 'production':
        app.run_server("0.0.0.0", debug=True, port=8050)
    else:
        app.run_server(debug=True, port=8050)
