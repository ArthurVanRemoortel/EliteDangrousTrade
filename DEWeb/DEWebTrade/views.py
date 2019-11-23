from django.shortcuts import render
from django.http import HttpResponse
from .forms import RunForm, ItemForm
from pprint import pprint
from TradeDangerous.tradedangerous import commands, tradedb
from TradeDangerous import tradedangerous
# import requests
import os
import sqlite3
from pprint import pprint
from collections import namedtuple

tdb = tradedb.TradeDB()
buying = tdb.getAverageBuying()
selling = tdb.getAverageSelling()

Row = namedtuple('Row', 'station price demand age dist')


class ItemWrapper(object):
    def __init__(self, td_item):
        """

        :type td_item: tradedb.Item
        """
        self.id = td_item.ID
        self.td_item = td_item
        self.name = td_item.dbname
        self.category = td_item.category
        self.avgPrice = td_item.avgPrice

    @property
    def avg_selling(self):
        return selling[self.id]

    @property
    def avg_buying(self):
        return buying[self.id]

    def max_selling(self):
        return 0

    def __str__(self):
        return self.name


class StationWrapper(object):
    def __init__(self, td_station):
        """
        :type td_station: tradedb.Station
        """
        self.id = td_station.ID
        self.td_station = td_station
        self.name = td_station.dbname
        self.dataAge = td_station.dataAge

    def __str__(self):
        return self.name


ALL_ITEMS = {item.ID: ItemWrapper(item) for item in tdb.items()}


def main(request):
    return render(request, 'main.html', {})


def items(request):
    return render(request, 'items.html', {'items': ALL_ITEMS.values()})


def item(request, item_id, near_system=None):
    item = ALL_ITEMS[item_id]
    if request.method == 'GET':
        form = ItemForm(request.POST)
    elif request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['from_system']:
                near_system = form.cleaned_data['from_system']

    if near_system:
        distance = 100
        min_price = 0
        command = f'trade.py sell ' + f'{item.name.replace(" ", "")} --near {near_system.replace(" ", "")} --ly {distance} --price-sort --gt {min_price} --limit 50'
    else:
        command = f'trade.py sell ' + f'{item.name.replace(" ", "")} --price-sort --limit 50'
    print(command)
    cmdIndex = commands.CommandIndex()
    cmdenv = cmdIndex.parse(command.split(' '))
    rows = []
    try:
        results = cmdenv.run(tradedb.TradeDB(cmdenv, load=cmdenv.wantsTradeDB))
        print(results.render())
        for row in results.rows:
            station = row.station
            price = "{:,}".format(row.price)
            demand = row.demand
            age = row.age
            try:
                dist = '%.2f' % row.dist
            except AttributeError:
                dist = None
            rows.append(Row(station, price, demand, age, dist))
    finally:
        # always close tdb
        tdb.close()
    return render(request, 'item.html', {'item': item, 'rows': rows, 'form': form, 'all_systems': tdb.systems()})


def run(request):
    form = None
    results = None
    if request.method == 'GET':
        form = RunForm(request.POST)
    elif request.method == 'POST':
        form = RunForm(request.POST)

        if form.is_valid():
            print("IS VALID")
            pprint(form.cleaned_data)
            # forced_command = form.cleaned_data['forced_command']
            #
            # from_system = form.cleaned_data['from_system']
            # from_station = form.cleaned_data['from_station']
            #
            # to_type = form.cleaned_data['to_type']
            # to_system = form.cleaned_data['to_system']
            # to_station = form.cleaned_data['to_station']
            #
            # via_system = form.cleaned_data['via_system']
            # via_station = form.cleaned_data['via_station']
            #
            # hops_type = form.cleaned_data['hops_type']
            # hops_n = form.cleaned_data['hops_n']
            # do_loop = form.cleaned_data['do_loop']
            # loop_n = form.cleaned_data['loop_n']
            # end_jumps = form.cleaned_data['end_jumps']
            # credits = form.cleaned_data['credits']
            # cargo = form.cleaned_data['cargo']
            # ly = form.cleaned_data['ly']

            input_data = {}
            command = ""
            for form_field, form_data in form.cleaned_data.items():
                if form_field is 'forced_command' and form_data:
                    input_data[form_field] = form_data
                    command = ' ' + form_data
                    break
                else:
                    input_data[form_field] = form_data
                    if form_field is 'from_system' and form_data:
                        args = f'--fr={form_data.replace(" ", "")}'
                        station = form.cleaned_data['from_station']
                        if station:
                            args += f'/"{station.replace(" ", "")}"'
                        command += ' '+args

                    if form_field is 'to_type':
                        args = ''
                        to_system = form.cleaned_data['to_system']
                        to_station = form.cleaned_data['to_station']
                        if form_data == str(0):
                            args += '--to='
                        else:
                            args += '--towards='
                        if to_system:
                            args += f'{to_system.replace(" ", "")}'
                            if to_station:
                                args += f'/"{to_station.replace(" ", "")}"'
                            command += ' ' + args

                    if form_field is 'via_system':
                        args = ''
                        via_system = form_data
                        via_station = form.cleaned_data['via_station']
                        if via_system:
                            args += "--via="
                            args += f'"{via_system.replace(" ", "")}"'
                            if via_station:
                                args += f'/"{via_station.replace(" ", "")}"'
                            command += ' ' + args

                    if form_field is 'hops_type':
                        args = ''
                        if form_data == str(0):
                            hops = form.cleaned_data['hops_n']
                            args += '--hops '
                            args += str(hops)
                        else:
                            args += '--direct'
                        if args:
                            command += ' ' + args

                    if form_field is 'do_loop':
                        args = ''
                        if form_data:
                            args += '--loop'
                            command += ' ' + args

                    if form_field is 'loop_n':
                        args = ''
                        if form_data:
                            args += "--loop-int " + str(form_data)
                            command += ' ' + args

                    if form_field is 'end_jumps':
                        args = ''
                        if form_data:
                            args += "--end-jumps " + str(form_data)
                            command += ' ' + args

                    if form_field is 'credits':
                        args = ''
                        if form_data:
                            args += "--cr=" + str(form_data)
                            command += ' ' + args

                    if form_field is 'cargo':
                        args = ''
                        if form_data:
                            args += "--cap=" + str(form_data)
                            command += ' ' + args

                    if form_field is 'ly':
                        args = ''
                        if form_data:
                            args += "--ly-per " + str(form_data)
                            command += ' ' + args

            command = 'trade.py run' + command
            print(command)
            cmdIndex = commands.CommandIndex()
            cmdenv = cmdIndex.parse(command.split(' '))
            tdb = tradedb.TradeDB(cmdenv, load=cmdenv.wantsTradeDB)
            try:
                results = cmdenv.run(tdb)
            finally:
                # always close tdb
                tdb.close()

        else:
            print("Form is not valid")
            pprint(form.errors)

    routes_rows = []
    if results:
        routes = results.data
        for i in range(min(len(routes), cmdenv.routes)):
            print(routes[i].detail(cmdenv))
            routes_rows.append(routes[i].detail(cmdenv))

    context = {'form': form, 'routes_rows': routes_rows}

    return render(request, 'run.html', context)