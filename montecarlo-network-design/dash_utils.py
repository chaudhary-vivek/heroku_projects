import dash_bootstrap_components as dbc


def make_card(alert_message, color, cardbody, style_dict = None):
    return  dbc.Card([  dbc.Alert(alert_message, color=color)
                        ,dbc.CardBody(cardbody)
                    ], style = style_dict)#end card

