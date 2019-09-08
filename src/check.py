#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import sys

def main(input_file, output_file):
    global priority_order_take
    print('Input file: ' + input_file)
    print('Output file: ' + output_file)
    couriers, orders, depots = load_data(input_file)


    with open(output_file, 'r') as f:
        output_data = json.load(f)
    taken_orders = []
    complete_orders = []
    while len(complete_orders) < len(orders):
        for step, event in enumerate(output_data):
            courier_id = event['courier_id']
            action = event['action']
            point_id = event['point_id']
            courier = couriers[courier_id]
            point = depots[point_id]

            # Последнее местоположение курьера
            courier_location = courier['location']
            min_time = 10000
            priority_order = 0
            priority_order_drop = 0
            priority_order_take = 0
            for i, order1 in orders.items():
                open_time = order1["pickup_from"]
                x0 = courier_location[0]
                y0 = courier_location[1]
                x1 = order1["pickup_location_x"]
                y1 = order1["pickup_location_y"]
                x2 = order1["dropoff_location_x"]
                y2 = order1["dropoff_location_y"]
                travel_time = 10 + (abs(x0 - x1) + abs(y0 - y1))
                travel_time2 = 10 + (abs(x0 - x2) + abs(y0 - y2))
                if (courier["time"] + travel_time) <= order1["pickup_to"] and not (order1 in taken_orders):
                    wait_time = abs(open_time - (courier["time"] + travel_time))
                    time = travel_time + wait_time
                    if time <= min_time:
                        priority_order_take = order1
                        min_time = time
                if (courier["time"] + travel_time2) <= order1["dropoff_to"] and order1 in taken_orders and not (
                        order1 in complete_orders):

                    wait_time = abs(open_time - (courier["time"] + travel_time2))
                    time = travel_time2 + wait_time
                    if time <= min_time:
                        priority_order_drop = order1
                        min_time = time
            if priority_order_take != 0:
                taken_orders.append(priority_order_take)
                priority_order = priority_order_take
                print("take")
            elif priority_order_drop != 0:
                complete_orders.append(priority_order_drop)
                priority_order = priority_order_drop
                print("drop")
            print(priority_order)
            if priority_order != 0:
                order_id = priority_order['order_id']
                order = orders[order_id]
                # Местоположение точки назначения, куда направляется курьер
                destination_location = [priority_order["pickup_location_x"], priority_order["pickup_location_y"]]
                print(destination_location)
                # Время перемещения до точки назначения
                duration_minutes = get_travel_duration_minutes(courier_location, destination_location)
                # Самое раннее время, в которое курьер может оказаться на точке назначения
                visit_time = courier['time'] + duration_minutes
                courier["time"] = visit_time

                if visit_time < point['timewindow'][0]:
                    # Если курьер прибывает раньше левой границы временного интервала на точке, то он ждет начала интервала
                    visit_time = point['timewindow'][0]
                elif visit_time > point['timewindow'][1]:
                    # Если курьер прибывает позже правой границы временного интервала на точке, то это опоздание
                    raise Exception('Courier will be late')

                if action == 'pickup':
                    # Если order_id сейчас не в точке point_id, то ошибка
                    """if 'order_time' not in point or order_id not in point['order_time']:
                        raise Exception('Cant pickup')
                    # Если курьер едет за заказом на склад, то, возможно, ему нужно будет подождать появления этого заказа на складе
                    if is_depot_point(point_id) and visit_time < point['order_time'][order_id]:
                        visit_time = point['order_time'][order_id]"""
                    # Курьер забрал заказ, удаляем информацию о том, с какого времени заказ находится в этой точке
                    point.pop('order_time', None)
                elif action == 'dropoff':
                    # Если point_id, не id склада или id точки dropoff заказа order_id, то ошибка (курьер привез заказ не туда)
                    """if not is_depot_point(point_id) and (point_id != order['dropoff_point_id']):
                        raise Exception('Cant dropoff')"""

                    # Добавляем информацию о времени появления заказа на точке
                    point['order_time'] = {}
                    point['order_time'][order_id] = visit_time
                else:
                    raise Exception('Unknown action')

                # Обновляем время и местоположение курьера
                courier['time'] = visit_time
                courier['location'] = destination_location



    # Проверяем, что курьеры выполнили все заказы, которые взяли
    # И посчитаем общую стоимость выполненных заказов
    has_unfinished_orders = False
    orders_payment = 0
    print(complete_orders)
    print(taken_orders)
    for order_id, order in orders.items():
        pickup_point_id = order['pickup_point_id']
        dropoff_point_id = order['dropoff_point_id']
        orders_payment += order['payment']

    # Считаем общую продолжительность работы курьера в минутах
    work_duration = sum([x['time'] - 360 for x in couriers.values()])
    work_payment = work_duration * 2
    profit = orders_payment - work_payment

    print('Total orders payment: {}'.format(orders_payment))
    print('Total couriers payment: {}'.format(work_payment))
    print('Profit: {}'.format(profit))


def load_data(file):
    """Загрузка входных данных из файла"""
    with open(file, 'r') as f:
        input_data = json.load(f)
    couriers = {}
    orders = {}
    points = {}
    for depotData in input_data['depots']:
        points[depotData['point_id']] = {
            'location': [depotData['location_x'], depotData['location_y']],
            'timewindow': [0, 1439],
        }
    for courierData in input_data['couriers']:
        couriers[courierData['courier_id']] = {
            'location': [courierData['location_x'], courierData['location_y']],
            'time': 360,
        }
    for orderData in input_data['orders']:
        points[orderData['pickup_point_id']] = {
            'location': [orderData['pickup_location_x'], orderData['pickup_location_y']],
            'timewindow': [orderData['pickup_from'], orderData['pickup_to']],
            'order_time': {orderData['order_id']: orderData['pickup_from']}
        }
        points[orderData['dropoff_point_id']] = {
            'location': [orderData['dropoff_location_x'], orderData['dropoff_location_y']],
            'timewindow': [orderData['dropoff_from'], orderData['dropoff_to']],
        }
        orders[orderData['order_id']] = orderData
    return couriers, orders, points


def get_travel_duration_minutes(location1, location2):
    """Время перемещения курьера от точки location1 до точки location2 вминутах"""
    distance = abs(location1[0] - location2[0]) + abs(location1[1] - location2[1])
    return 10 + distance


def is_depot_point(point_id):
    """Является ли $pointId точкой склада"""
    return 30001 <= point_id <= 40000


if __name__ == '__main__':
    example_dir = os.path.dirname(os.path.abspath(__file__)) + '/../example'
    input_file = example_dir + '/input.json'
    output_file = example_dir + '/output.json'
    if len(sys.argv) > 2:
        input_file = sys.argv[1]
        output_file = sys.argv[2]


    main(input_file, output_file)
