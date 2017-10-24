import json
import pandas as pd

from django.shortcuts import render, render_to_response

from bokeh.plotting import figure, ColumnDataSource, show
from bokeh.embed import components
from bokeh.layouts import widgetbox, layout, column
from bokeh.models.widgets import Button, RadioButtonGroup, Select
from bokeh.models import HoverTool, CustomJS
from svgpathtools import svg2paths2
from bokeh.models import Range1d


def index(request):
    x = [1, 3, 5, 7, 9, 11, 13]
    y = [1, 2, 3, 4, 5, 6, 7]
    title = 'y = f(x)'

    plot = figure(title=title,
                  x_axis_label='X-Axis',
                  y_axis_label='Y-Axis',
                  plot_width=400,
                  plot_height=400)

    plot.line(x, y, legend='f(x)', line_width=2)
    # Store components
    script, div = components(plot)
    variables = {'script': script, 'div': div}
    # Feed them to the Django template.
    return render(request=request, template_name='index.html',
                  context=variables)


def general_plot(request):
    # List of tools to enable
    tools = "pan,reset,save,wheel_zoom,box_zoom"

    title = 'Generic Plotting'
    x = [10, 20, 30, 40, 50]
    y = [100, 200, 300, 400, 500]
    source = ColumnDataSource(data=dict(
        x=[1, 2, 3, 4, 5],
        y=[10, 20, 30, 40, 50],
        desc=['A', 'B', 'C', 'D', 'E']
    ))

    hover = HoverTool(tooltips=[
        ("index", "$index"),
        ("(x,y)", "($x,$y)"),
        ("desc", "@desc"),
    ])

    title = title

    jscode = """
        console.log("In callable");
        var data = source.data;
        x = data['x'];
        console.log(x)
        y = data['y'] * 0;
        source.change.emit();
        """

    jscode2 = """
        var urlstring = "http://127.0.0.1:8000/IWI/player/graphanalytics/?investment_id=zinc,year=1990"
        var data = zincData
        window.location = urlstring; 
    """

    callback = CustomJS(args=dict(source=source), code=jscode)
    callback2 = CustomJS(args=dict(source=source), code=jscode2)

    # Creating some of the wid  gets
    select_xaxis = Select(title="X-Axis:", value="foo", options=["foo", "bar", "baz", "quux"])
    select_yaxis = Select(title="Y-Axis:", value="foo", options=["foo", "bar", "baz", "quux"])
    button_plot = Button(label="Plot", callback=callback2)
    # button_plot.on_click(CustomJS(args=dict(source=source), code=jscode))

    widgets = widgetbox(select_xaxis, select_yaxis, button_plot, width=300)

    x_axis_label = select_xaxis.value
    y_axis_label = select_yaxis.value
    plot = figure(x_axis_label=x_axis_label, y_axis_label=y_axis_label, title=title, plot_width=400, plot_height=400,
                  tools=tools)
    plot.line('x', 'y', line_width=2, source=source, legend='Test')
    plot.add_tools(hover)

    graph_layout = layout([[plot], [widgets]])

    script, div = components(graph_layout)
    variables = {'script': script, 'div': div}

    return render(request=request, template_name='general_plot.html', context=variables)


def world_plot(request):
    paths, attributes, svg_attributes = svg2paths2('static_resources/worldIndiaHigh.svg')
    country_names = [attribute['title'] for attribute in attributes]
    country_patches = []

    for attribute, path in zip(attributes, paths):
        if attribute['class'] == 'land':
            for path in paths:
                country_xs = []
                country_ys = []
                for line in path:
                    start, end = line
                    country_xs.append(start.real)
                    country_ys.append(end.real)
            country_patches.append([country_xs, country_ys])

    patch = country_patches[0]
    print("Patch: ", patch)

    p = figure(plot_width=500, plot_height=500, x_axis_location=None, y_axis_location=None)
    source = ColumnDataSource(data=dict(
        x=country_patches[0],
        y=country_patches[1]
        # name=country_names
    ))
    # hover = HoverTool(tooltips=[
    #     ("desc", "@desc"),
    # ])
    # p.add_tools(hover)
    p.grid.grid_line_color = None
    # p.patches(country_patches)
    # p.patches(xs=country_patches[0], ys=country_patches[1], fill_color='white')
    p.patches('x', 'y', source=source, line_width=0.2, fill_color='white')

    # for attribute, path in zip(attributes, paths):
    #     if attribute['class'] == 'land':
    #         print(attribute['title'], path)

    script, div = components(p)
    variables = {'script': script, 'div': div}
    return render(request=request, template_name='world_plot.html', context=variables)


def world_plot_json(request):
    with open('static_resources/countries.geo.json') as json_data:
        countries = json.load(json_data)

        countryObject = {}
        for country in countries['features']:
            if country['geometry']['coordinates'] == 1:
                countryObject[country['properties']['name']] = {
                    'x': [x[0] for x in country['geometry']['coordinates'][0]],
                    'y': [x[1] for x in country['geometry']['coordinates'][0]],
                }
            else:
                countryObject[country['properties']['name']] = {
                    'x': [x[0] for x in item['geometry']['coordinates'][0] for item in country['geometry']['coordinates']],
                    'y': [x[1] for x in item['geometry']['coordinates'][0] for item in country['geometry']['coordinates']],
                }
    df = pd.DataFrame(countryObject)
    p = figure(plot_width=1000, plot_height=500, x_axis_location=None, y_axis_location=None)
    p.grid.grid_line_color = None
    hover = HoverTool(tooltips=[
        ("(x,y)", "($x, $y)"),
        ("Name:", '@name'),
        ("ID:", '@id'),
    ])
    p.add_tools(hover)
    for (index, country) in enumerate(df):
        p.patch(
            x=df[country]['x'],
            y=df[country]['y'],
            alpha=.6
        )
    p.x_range = Range1d(start=-180, end=180)
    p.y_range = Range1d(start=-90, end=90)

    script, div = components(p)
    variables = {'script': script, 'div': div}
    return render(request=request, template_name='world_plot.html', context=variables)
