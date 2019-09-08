import json
import os
import sys

def main(input_file, output_file):
    global priority_order_take
    global output1
    output1 = []
    print('Input file: ' + input_file)
    print('Output file: ' + output_file)
    couriers, orders, depots = load_data(input_file)


    with open(output_file, 'r') as f:
        output_data = json.load(f)
    taken_orders = []
    complete_orders = []
    failed_orders = []
    a = False
    while (len(complete_orders) < len(orders)) and not(a):
        for step, event in enumerate(output_data):
            #courier_id = event['courier_id']
            #ction = event['action']
            #point_id = event['point_id']
            courier = couriers[1]

            # Последнее местоположение курьера
            courier_location = courier['location']
            min_time = 10000
            priority_order = 0
            priority_order_drop = 0
            priority_order_take = 0
            for i, order1 in orders.items():
                open_time = order1["pickup_from"]
                open_time2 = order1["dropoff_from"]
                x0 = courier_location[0]
                y0 = courier_location[1]
                x1 = order1["pickup_location_x"]
                y1 = order1["pickup_location_y"]
                x2 = order1["dropoff_location_x"]
                y2 = order1["dropoff_location_y"]
                travel_time = 10 + (abs(x0 - x1) + abs(y0 - y1))
                travel_time2 = 10 + (abs(x0 - x2) + abs(y0 - y2))
                if (courier["time"] + travel_time) <= order1["pickup_to"] and not (order1 in taken_orders):
                    if open_time - (courier["time"] + travel_time2) < 0:
                        wait_time = abs(travel_time)
                    else:
                        wait_time = abs(open_time - (courier["time"] + travel_time))
                    time = travel_time + wait_time
                    if time <= min_time:
                        priority_order_take = order1
                        min_time = time
                elif (courier["time"] + travel_time2) <= order1["dropoff_to"] and order1 in taken_orders and not (order1 in complete_orders):
                    if open_time2 - (courier["time"] + travel_time2) < 0:
                        wait_time = abs(travel_time2)
                    else:
                        wait_time = abs(open_time2 - (courier["time"] + travel_time2))
                    time = travel_time2 + wait_time
                    if time <= min_time:
                        priority_order_drop = order1
                        min_time = time
                elif courier["time"] +500 >= order1["dropoff_to"] and order1 in taken_orders and not (order1 in complete_orders):
                    priority_order_drop = order1

            if priority_order_take != 0:
                taken_orders.append(priority_order_take)
                priority_order = priority_order_take
                print("take")
                order_id = priority_order['order_id']
                order = orders[order_id]
                # Местоположение точки назначения, куда направляется курьер
                destination_location = [priority_order["pickup_location_x"], priority_order["pickup_location_y"]]
                print(destination_location)
                print(courier_location)
                # Время перемещения до точки назначения
                duration_minutes = get_travel_duration_minutes(courier_location, destination_location)
                # Самое раннее время, в которое курьер может оказаться на точке назначения
                print(duration_minutes)
                visit_time = courier['time'] + duration_minutes

                if visit_time > priority_order["dropoff_to"]:
                    # Если курьер прибывает позже правой границы временного интервала на точке, то это опоздание
                    # raise Exception('Courier will be late')
                    failed_orders.append(priority_order)


                # Обновляем время и местоположение курьера
                courier['time'] = courier["time"] + duration_minutes
                courier['location'] = destination_location


            elif priority_order_drop != 0:
                complete_orders.append(priority_order_drop)
                priority_order = priority_order_drop
                print("drop")
                order_id = priority_order['order_id']
                order = orders[order_id]
                # Местоположение точки назначения, куда направляется курьер
                destination_location = [priority_order["dropoff_location_x"], priority_order["dropoff_location_y"]]
                print(destination_location)
                print(courier_location)
                # Время перемещения до точки назначения
                duration_minutes = get_travel_duration_minutes(courier_location, destination_location)
                print(duration_minutes)
                # Самое раннее время, в которое курьер может оказаться на точке назначения
                visit_time = courier['time'] + duration_minutes


                # Обновляем время и местоположение курьера
                courier['time'] = courier["time"] + duration_minutes
                courier['location'] = destination_location
            else:
                a = True
            #print(priority_order)
            #print(courier["time"])
            #print(courier["location"])
            if priority_order_drop != 0:
                 add(1,"dropoff",priority_order_drop["order_id"],priority_order_drop["dropoff_point_id"])
            elif priority_order_take != 0:
                add(1,"pickup",priority_order_take["order_id"],priority_order_take["pickup_point_id"])






    # Проверяем, что курьеры выполнили все заказы, которые взяли
    # И посчитаем общую стоимость выполненных заказов
    has_unfinished_orders = False
    orders_payment = 300000
    print(complete_orders)
    print(taken_orders)
    print(failed_orders)
    for order in complete_orders:
        pickup_point_id = order['pickup_point_id']
        dropoff_point_id = order['dropoff_point_id']
        orders_payment += order['payment']

    # Считаем общую продолжительность работы курьера в минутах
    work_duration = sum([x['time'] - 360 for x in couriers.values()]) + loo
    work_payment = work_duration
    profit = orders_payment - work_payment

    print('Total orders payment: {}'.format(orders_payment))
    print('Total couriers payment: {}'.format(work_payment))
    print('Profit: {}'.format(profit))




def add(courier_id, action, order__id, point_id):
 with open(output_file, mode='w+', encoding='utf-8') as feedsjson:
    """feeds = json.load(feedsjson)"""
    entry = {'courier_id': courier_id, 'action': action, 'order__id': order__id, 'point_id': point_id}
    output1.append(entry)
    json.dump(output1, feedsjson)


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
    example_dir = os.path.dirname(os.path.abspath(__file__)) + '/../data'
    input_file = example_dir + '/ref.json'
    example_dir = os.path.dirname(os.path.abspath(__file__)) + '/../example'
    output_file = example_dir + '/output.json'
    if len(sys.argv) > 2:
        input_file = sys.argv[1]
        output_file = sys.argv[2]


    main(input_file, output_file)