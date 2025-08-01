import plotly.graph_objects as go


def make_xas_plot(title, x, x_label, y_list, y_label):
    fig = go.Figure().update_layout(
        title_text=title,
    )
    if x is None or y_list is None or len(y_list) < 1:
        return fig
    for y in y_list:
        fig.add_traces(
            go.Scatter(
                name=y_label,
                x=x,
                y=y,
                mode='lines',
                hoverinfo='x+y+name',
            )
        )

    x_unit = getattr(x, 'units', None)
    x_unit_str = f'{x_unit:~P}' if x_unit else 'a.u.'
    y_unit = getattr(y_list[0], 'units', None)
    y_unit_str = f'{y_unit:~P}' if y_unit else 'a.u.'
    fig.update_layout(
        title_text=title,
        xaxis={
            'fixedrange': False,
            'title': f'{x_label} ({x_unit_str})',
        },
        yaxis={
            'fixedrange': False,
            'title': f'{y_label} ({y_unit_str})',
        },
        hovermode='x unified',
    )
    return fig
