# описание нашего алгоритма

Работа курьера начинается с того, что приложение указывает самый оптимальный маршрут до точки по времени в пути, времени до открытия точки и времени закрытия.
Время закрытия учитывается для того, чтобы курьер не опоздал на точку.
Затем точка бронируется, чтобы избежать пересечения двух курьеров.
После прибытия на точку курьера алгоритм повторяется, а данная точка удаляется, чтобы в будущем не приехать на нее еще раз.

----------------------------------------------------------------------------------------------------------------------------------
алгоритм оптимального пути - времени закрытия точки > время в пути + время до открытия точки < остальных точек этого же алгоритма
----------------------------------------------------------------------------------------------------------------------------------
