'''Программа генерации акустических помех 
типа "одноголосная речеподобная помеха" и "речевой хор" 
из аудиофайлов формата .wav
Версия 1.0 (c графическим интерфейсом пользователя)
'''
# Импорты модулей стандартной библиотеки.
import audioop
import random
import struct
import tkinter
import tkinter.filedialog
import tkinter.messagebox
import time
import wave
import winsound
# Импорты сторонних модулей. 
import numpy
import pyaudio 
import matplotlib.pyplot


class SpeechLikeSignal:
    '''Класс для обработки аудиофайлов формата .wav
    с целью генерации на их основе акустических помех
    '''
    # Создание буфера для хранения объектов класса.
    class_object_buffer = []
    # Число фреймов (амплитудных отсчётов),
    # которые содержит базовый фрагмент,
    # используемый для генерации помехи. 
    total_fragment_nframes = None
    # Общее число фреймов в итоговом помеховом сигнале.
    total_nframes = None
    # Число пакетов фреймов в помеховом сигнале.
    total_package_number = None
    # Частота дискретизации помехового сигнала.
    total_frame_rate = 22050
    # Формат кодирования помехового сигнала (число байт на фрейм).
    total_sampwidth = 2
    # Число каналов помехового сигнала.
    total_nchannels = 1
    # Масштабирующий коэффициент суммирования сигналов.
    scale_factor = None
    # Флаг конвертации для модуля struct.
    struct_flag = None
    # Флаг типа массива для модуля numpy.
    numpy_flag = None
    # Флаг формата данных для модуля pyaudio.
    pyaudio_flag = pyaudio.paInt16
    # Выходные данные в байтовом формате.
    output_data_byte = None
    
    def __init__(self, file_name):
        '''Инициализация объекта класса'''
        # Определение имени объекта класса.
        self.name = file_name
        # Чтение информации об объекте класса.
        self.data = wave.open(file_name, 'rb')
        # Определение числа фреймов.
        self.nframes = self.data.getnframes()
        # Определение числа каналов.
        self.nchannels = self.data.getnchannels()
        # Определение частоты дискретизации.
        self.frame_rate = self.data.getframerate()
        # Определение формата кодирования.
        self.sampwidth = self.data.getsampwidth()
        # Получение фреймов аудиофайла в виде строки байт.
        self.data_byte = self.data.readframes(self.nframes)
        # Создание копии фреймов исходного аудиофайла
        # для возможной последующей конвертации.
        self.data_byte_convertion = self.data_byte
        # Запуск тестирующего метода,
        # который проверяет соответствие параметров файла требуемым
        # и при необходимости производит конвертацию.
        self.testing_function()

    def interface_function():
        '''Метод класса, предназначенный для получения входных данных'''
        # Получение требуемой частоты дискретизации
        # из виджета графического интерфейса.
        SpeechLikeSignal.total_frame_rate = frame_rate_radiobutton_flag.get()
        # Получение требуемого числа каналов
        # из виджета графического интерфейса.
        SpeechLikeSignal.total_nchannels = nchannels_radiobutton_flag.get()
        # Получение формата кодирования
        # из виджета графического интерфейса.
        SpeechLikeSignal.total_sampwidth = sampwidth_radiobutton_flag.get()
        # Получение длительности звукового фрагмента,
        # используемого для генерации помехи.
        fragment_time = int(fragment_time_entry.get()) / 1000
        # Вычисление числа фреймов, 
        # необходимых для формирования звукового фрагмента
        # длительностью fragment_time.
        SpeechLikeSignal.total_fragment_nframes = round(
            fragment_time * SpeechLikeSignal.total_frame_rate
            )
        # Получение длительности помехового сигнала
        # из виджета графического интерфейса.
        total_time = int(total_time_entry.get())
        # Вычисление числа пакетов фреймов,
        # необходимых для формирования помехового сигнала
        # длительностью total_time.
        SpeechLikeSignal.total_package_number = round(
            total_time/fragment_time
            )
        # Вычисление общего числа фреймов в помеховом сигнале.
        SpeechLikeSignal.total_nframes = (
            SpeechLikeSignal.total_package_number 
            * SpeechLikeSignal.total_fragment_nframes
            )    
        # Присвоение флагов для модулей:
        # struct (флаг конвертации),
        # numpy(флаг типа массива),
        # pyaudio (флаг формата).
        if SpeechLikeSignal.total_sampwidth == 2:
            SpeechLikeSignal.struct_flag = 'h'
            SpeechLikeSignal.numpy_flag = numpy.int16
            SpeechLikeSignal.pyaudio_flag = pyaudio.paInt16
        elif SpeechLikeSignal.total_sampwidth == 4:
             SpeechLikeSignal.struct_flag = 'i'
             SpeechLikeSignal.numpy_flag = numpy.int32
             SpeechLikeSignal.pyaudio_flag = pyaudio.paInt32    
            
    def create_instance_function():
        '''Метод класса, предназначенный для создания объектов'''
        # Определение значения 
        # масштабирующего коэффициента суммирования сигналов.
        SpeechLikeSignal.scale_factor = len(file_ways_buffer)
        # Создание объектов класса и добавление их в буфер для хранения.
        for file_name in file_ways_buffer:
            SpeechLikeSignal.class_object_buffer.append(
                SpeechLikeSignal(file_name)
                )

    def testing_function(self):
        '''Метод объекта, 
        проверяющий соответствие исходных параметров объекта 
        заданным параметрам помехи
        '''
        # Проверка на соотвествие частот дискретизации,
        # формата кодирования и числа каналов.
        # При несоответствии - запуск методов конвертации
        # (все процессы обработки аудиозаписей
        # производятся в моноформате,
        # при необходимости конвертация в стереоформат
        # осуществляется перед записью выходных данных).
        if self.frame_rate != SpeechLikeSignal.total_frame_rate:
            self.convertion_frame_rate()
        if self.sampwidth != SpeechLikeSignal.total_sampwidth:
            self.convertion_sampwidth()
        if self.nchannels == 2:
            self.convertion_nchannels_to_mono()             
    
    def convertion_frame_rate(self):
        '''Метод объекта, 
        осуществляющий конвертацию частоты дискретизации
        '''
        self.data_byte_convertion = audioop.ratecv(
            self.data_byte_convertion,
            self.sampwidth,
            self.nchannels,
            self.frame_rate,
            SpeechLikeSignal.total_frame_rate,
            None
            )[0]
        
    def convertion_sampwidth(self):
        '''Метод объекта,
        осуществляющий конвертацию формата кодирования
        '''
        self.data_byte_convertion = audioop.lin2lin(
            self.data_byte_convertion,
            self.sampwidth,
            SpeechLikeSignal.total_sampwidth
            )

    def convertion_nchannels_to_mono(self):
        '''Метод объекта, осуществляющий конвертацию в моноформат'''
        self.data_byte_convertion = audioop.tomono(
            self.data_byte_convertion,
            SpeechLikeSignal.total_sampwidth,
            1, 0
            )
        
    def convertion_nchannels_to_stereo(data_byte):
        '''Метод класса, осуществляющий конвертацию в стереоформат'''
        data_byte_convertion = audioop.tostereo(
            data_byte,
            SpeechLikeSignal.total_sampwidth,
            1, 1
            )
        return data_byte_convertion
    
    def start_object_processing():
        '''Метод класса,
        предназначенный для запуска процесса обработки объектов
        '''
        for instance in SpeechLikeSignal.class_object_buffer:
            instance.object_processing()

    def object_processing(self):
        '''Метод объекта, осуществляющий процесс обработки''' 
        # Преобразование конвертированных фреймов объекта
        # в целочисленный формат.
        self.data_format_converter()
        # Разбиение целочисленных фреймов
        # на пакеты длиной total_fragment_nframes.
        self.packets_generating()
        # Фильтрация пакетов,
        # которые не содержат формантных составляющих.
        self.packets_filtration()
        # Масштабирование пакетов.
        self.scale_function()

    def data_format_converter(self):
        '''Метод объекта,
        осуществляющий преобразование конвертированных фреймов
        из байтового формата в целочисленный
        '''
        self.data_integer = struct.unpack(
            '<' + str(len(self.data_byte_convertion) 
            // SpeechLikeSignal.total_sampwidth) 
            + SpeechLikeSignal.struct_flag,
            self.data_byte_convertion
            )
    
    def packets_generating(self):
        '''Метод объекта,
        осуществляющий разбиение целочисленных фреймов
        на пакеты длиной fragment_nframes
        '''
        # Вычисление числа пакетов
        # для разбиения целочисленных фреймов
        # по total_fragment_nframes в каждом.
        self.packets_number = (
            len(self.data_integer) 
            // SpeechLikeSignal.total_fragment_nframes
            )
        # Вычленение требуемого числа фреймов, 
        # необходимых для заполнения пакетов.
        self.data_integer_for_pack = self.data_integer[
            :self.packets_number 
            * SpeechLikeSignal.total_fragment_nframes
            ]
        # Создание numpy массива фреймов с учётом формата кодирования 
        self.data_integer_array = numpy.array(
            self.data_integer_for_pack,
            dtype=SpeechLikeSignal.numpy_flag
            )
        # Изменение размера numpy массива c тем учётом,
        # чтобы каждая строка массива 
        # представляла из себя пакет фреймов.
        self.data_integer_packets = self.data_integer_array.reshape(
            self.packets_number,
            SpeechLikeSignal.total_fragment_nframes
            )

    def packets_filtration(self):
        '''Метод объекта,
        осуществляющий фильтрацию пакетов
        (методом превышения порогового уровня)
        '''
        # Создание буфера для хранения отфильтрованных пакетов.
        buffer = []
        # Вычисление порогового значения
        # (среди всех целочисленных значений фреймов
        # находится макимальное значение,
        # которое соответствует формантным составляющим).
        # Пороговое значение выбирается уровне 0.2 от макимального
        # (экспериментально определено, что при таком уровне
        # удаётся эффективно отфильтровать пакеты,
        # не содержащие формантных составляющих).
        treshold = 0.2 * self.data_integer_packets.max()
        # Процесс фильтрации.
        for i in range(self.packets_number):
            if self.data_integer_packets[i].max() > treshold:
                buffer.append(self.data_integer_packets[i])
        self.data_integer_packets_filtration = numpy.array(buffer)

    def scale_function(self):
        '''Метод объекта,
        предназначенный для масштабирования фреймов
        (для обеспечения возможности суммирования
        нескольких сигналов при формировании помехи
        типа "речевой хор")
        '''
        self.data_integer_packets_filtration_scale = (
            self.data_integer_packets_filtration 
            // SpeechLikeSignal.scale_factor
            )
    
    def create_output_data():
        '''Метод класса, формирующий выходные данные'''
        # Создание буфера для целочисленных выходных данных.
        output_data_integer = numpy.zeros(
            (SpeechLikeSignal.total_package_number,
            SpeechLikeSignal.total_fragment_nframes),
            dtype=SpeechLikeSignal.numpy_flag
            )
        # Заполнение буфера случайными отфильтрованными
        # и масштабированными пакетами объектов.
        for i in range(SpeechLikeSignal.total_package_number):
            for instance in SpeechLikeSignal.class_object_buffer:
                output_data_integer[i] += random.choice(
                    instance.data_integer_packets_filtration_scale
                    )
        # Преобразование буфера к одномерному виду.
        output_data_integer = output_data_integer.reshape(
            1, 
            SpeechLikeSignal.total_nframes
            ).ravel()
        # Конвертация целочисленных данных буфера в байтовый формат.
        SpeechLikeSignal.output_data_byte = struct.pack(
            '<' + str(SpeechLikeSignal.total_nframes) 
            + SpeechLikeSignal.struct_flag,
            *output_data_integer
            )
        # Конвертация байтовых данных в стереоформат
        # (при необходимости).
        if SpeechLikeSignal.total_nchannels == 2:
            SpeechLikeSignal.output_data_byte = (
                SpeechLikeSignal.convertion_nchannels_to_stereo(
                    SpeechLikeSignal.output_data_byte)
                    )

    def writing_output_file():
        '''Метод класса, записывающий выходные данные в аудиофайл'''
        # Указание пути для сохранения аудиофайла помехи.
        output_file_name = tkinter.filedialog.asksaveasfilename(
            filetypes=(("WAVE files", "*.wav"),
            ("All files", "*.*"))
            )
        # Открытие файла для записи.
        output_file = wave.open(output_file_name + '.wav','wb')
        # Определение параметров файла.
        output_file.setparams(
            (SpeechLikeSignal.total_nchannels,
            SpeechLikeSignal.total_sampwidth,
            SpeechLikeSignal.total_frame_rate,
            SpeechLikeSignal.total_nframes,
            'NONE',
            'not compressed')
            )
        # Запись выходных данных в аудиофайл
        output_file.writeframes(SpeechLikeSignal.output_data_byte) 
        # Закрытие файла.
        output_file.close()


# Графический интерфейс пользователя.
# Буфер хранения абсолютных путей к аудиофайлам.
file_ways_buffer = []
# Функции, описывающие события,
# происходящие по клику на кнопки интерфейса.
def get_help():
    '''Функция получения справки о работе программы
    (запускается нажатием кнопки "Справка"
    в строке меню)
    '''
    # Создание окна для отображения справки.
    help_window = tkinter.Toplevel()
    help_window.title('Справка')
    help_window.resizable(False, False)
    # Добавление многострочного текстового поля.
    help_text = tkinter.Text(help_window, width=110)
    help_text.pack(side=tkinter.LEFT)
    # Добавление скроллера в многострочное текстовое поле.
    scroll = tkinter.Scrollbar(help_window, command=help_text.yview)
    scroll.pack(side=tkinter.RIGHT, fill=tkinter.Y)
    help_text.config(yscrollcommand=scroll.set)
    # Вывод краткого руководства пользователя программой
    # в многострочное текстовое поле.
    with open('.\Help.txt', 'r') as help_file:
        # Счётчик позиции в многострочном текстовом поле
        # (формат: строка.столбец).
        i = 1.0
        # Считывание строк из текстового файла справки.
        help_str = help_file.readlines()
        # Удаление служебных символов 
        # и вставка строк в многострочное текстовое поле.
        for string in help_str:
            string.strip()
            help_text.insert(i, string)
            i += 1
    

def get_device_index():
    '''Функция получения списка доступных аудиоустройств
    (запускается нажатием кнопки button_get_device_index)
    '''
    # Создание окна для отображения информации
    # о подключенных аудиоустройствах.
    device_info_window = tkinter.Toplevel()
    device_info_window.title(
        'Информация о подключенных аудиоустройствах'
        )
    # Добавление многострочного текстового поля.
    device_text = tkinter.Text(device_info_window)
    device_text.pack()
    # Вставка и форматирование заголовка списка аудиоустройств.
    device_text.insert(1.0, 'Индекс   Название\n')
    device_text.tag_add('title', 1.0, '1.end')
    device_text.tag_configure(
        'title',
        font=('Times New Roman', 12, 'bold')
        )
    # Cоздание обьекта PyAudio.
    pyaudio_object = pyaudio.PyAudio()
    # Вывод списка доступных аудиоустройств
    # в многострочное текстовое поле.
    for i in range(0, pyaudio_object.get_device_count()):
        device_text.insert(
            float(i+2),
            str(i) + ' ' 
            + pyaudio_object.get_device_info_by_index(i)['name'] + '\n'
            )
    # Размещение окна в левом верхнем углу экрана.
    device_info_window.geometry('+0+0')


def voice_record_menu():
    '''Функция, создающая меню записи голоса
    (запускается нажатием кнопки button_voice_record_menu)
    '''
    
    def voice_recorder():
        '''Функция записи голоса
        (запускается нажатием кнопки button_start_record)
        '''
        # Проверка корректности данных,
        # введённых в текстовые поля графического интерфейса.
        try:
            int(record_time_entry.get())
        except ValueError:
            tkinter.messagebox.showerror(
                'Ошибка',
                'В поле продолжительности записи ' 
                + 'введены некорректные данные'
                )
            return        
        try:
            int(device_index_entry.get())
        except ValueError:
            tkinter.messagebox.showerror(
                'Ошибка',
                'В поле индекса аудиоустройства ' 
                + 'введены некорректные данные'
                )
            return        
        # Определение параметров записи.
        # Определение числа фреймов, считываемых за одну итерацию.
        chunk = 4096    
        # Получение частоты дискретизации
        # из виджета графического интерфейса.
        record_frame_rate = record_frame_rate_radiobutton_flag.get()
        # Получение формата кодирования
        # из виджета графического интерфейса.
        record_sampwidth = record_sampwidth_radiobutton_flag.get()
        # Присвоение флагов для модулей:
        # struct (флаг конвертации),
        # numpy (флаг типа массива),
        # pyaudio (флаг формата).
        if record_sampwidth == 2:
            record_pyaudio_flag = pyaudio.paInt16
            record_numpy_flag = numpy.int16
            record_struct_flag = 'h'
            plot_limit = 32768
        else:
            record_pyaudio_flag = pyaudio.paInt32
            record_numpy_flag = numpy.int32
            record_struct_flag = 'i'
            plot_limit = 214748368
        # Получение числа каналов
        # из виджета графического интерфейса.
        record_nchannels = record_nchannels_radiobutton_flag.get()
        # Определение продолжительности записи.
        record_time = int(record_time_entry.get())
        # Создание обьекта PyAudio.
        pyaudio_object = pyaudio.PyAudio()
        # Определение аудиоустройства,
        # с которого будет произведена запись.
        device_index = int(device_index_entry.get())
        # Открытие потока для записи
        # и определение его параметров.
        stream = pyaudio_object.open(
            format=record_pyaudio_flag,
            channels=record_nchannels,
            rate=record_frame_rate,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=chunk
            )
        # Открытие диалогового окна с информацией о начале записи.
        voice_recorder_info_window = tkinter.messagebox.showinfo(
            'Запись голоса',
            'Начинайте говорить после звукового сигнала'
            )
        # Визуализация процесса записи голоса.
        # Включение интерактивного режима интерфейса pyplot.
        matplotlib.pyplot.ion()
        # Создание рисунка(fig) и области рисования(ax).
        fig, ax = matplotlib.pyplot.subplots()
        # Установка параметров рисунка.
        fig.set_figwidth(12)
        fig.set_figheight(6)
        fig.canvas.set_window_title('Процесс записи голоса')
        # Размещение рисунка в центральной области экрана.
        fig.canvas.manager.window.geometry(
            '+{}+{}'.format(
                screen_width//4, 
                screen_height//4
                )
            )
        # Определение диапазона рисования по оси x.
        x = numpy.arange(0, chunk)
        # Рисование линии.
        line, = ax.plot(x, numpy.random.rand(chunk))
        # Определение параметров области рисования.
        ax.set_xlim(0, chunk)
        ax.set_ylim(-plot_limit, plot_limit)
        ax.set_title('Осцилограмма голоса')
        ax.set_xlabel('Номер фрейма')
        ax.set_ylabel('Амплитуда')
        # Генерация системного звукового сигнала начала записи.
        winsound.Beep(1000, 1000)
        # Задержка на 0,5 секунды
        # для недопущения записи остаточного системного звука.
        time.sleep(0.5)
        # Создание буфера для хранения записанных фреймов.
        buffer = []
        # Процесс записи голоса.
        for i in range(
                0, 
                int((record_frame_rate / chunk) 
                * record_time)):
            data = stream.read(chunk)
            buffer.append(data)
            # Конвертация в моноформат для отображения 
            # на области рисования.
            if record_nchannels == 2:
                data = audioop.tomono(data, record_sampwidth, 1, 0)
            data_integer = numpy.array(
                struct.unpack(
                    '<' + str(chunk) 
                    + record_struct_flag,
                    data
                    ),
                dtype=record_numpy_flag
                )
            # Обновление данных линии и холста рисунка
            # (такое обновление позволяет выводить данные
            # в режиме реального времени).
            line.set_ydata(data_integer)
            fig.canvas.draw()
            fig.canvas.flush_events()
        # Закрытие окна изуализации процесса записи голоса.
        matplotlib.pyplot.close()
        # Остановка и закрытие потока записи.
        stream.stop_stream()
        stream.close()
        pyaudio_object.terminate()
        # Получение пути и имени файла для сохранения записанных данных.
        voice_recorder_file_name = tkinter.filedialog.asksaveasfilename(
            filetypes=(("WAVE files", "*.wav"),
            ("All files", "*.*"))
            )
        # Проверка на непустой путь к файлу для сохранения данных.
        if not voice_recorder_file_name:
            voice_record_menu_window.destroy()
            return
        # Открытие файла в режиме записи данных.
        output_file = wave.open(voice_recorder_file_name + '.wav', 'wb')
        # Определение параметров файла.
        output_file.setparams(
            (record_nchannels,
            record_sampwidth,
            record_frame_rate,
            None,
            'NONE',
            'not compressed')
            )
        # Запись фреймов
        # с предварительным соединением между собой пакетов длиной chunk.
        output_file.writeframes(b''.join(buffer))
        # Закрытие файла. 
        output_file.close()
        # Закрытие окна меню записи голоса.
        voice_record_menu_window.destroy()

    # Создание окна меню записи голоса.
    voice_record_menu_window = tkinter.Toplevel()
    voice_record_menu_window.title('Меню записи голоса')
    # Создание и размещение метки частоты дискретизации.
    record_frame_rate_label = tkinter.Label(
        voice_record_menu_window,
        text='Частота дискретизации, Гц',
        font=('Times New Roman', 11)
        )
    record_frame_rate_label.grid(
        row=0,
        column=0, 
        sticky=tkinter.W
        )
    # Создание и размещение радиокнопок выбора частоты дискретизации.
    record_frame_rate_radiobutton_flag = tkinter.IntVar()
    record_frame_rate_radiobutton_flag.set(22050)
    record_frame_rate_radiobutton_1 = tkinter.Radiobutton(
        voice_record_menu_window,
        text='22050',
        font=('Times New Roman', 11),
        variable=record_frame_rate_radiobutton_flag,
        value=22050
        )
    record_frame_rate_radiobutton_2 = tkinter.Radiobutton(
        voice_record_menu_window,
        text='44100',
        font=('Times New Roman', 11),
        variable=record_frame_rate_radiobutton_flag,
        value=44100)
    record_frame_rate_radiobutton_1.grid(
        row=1,
        column=0,
        sticky=tkinter.W)
    record_frame_rate_radiobutton_2.grid(
        row=2,
        column=0,
        sticky=tkinter.W)
    # Создание и размещение метки формата кодирования.
    record_sampwidth_label = tkinter.Label(
        voice_record_menu_window,
        text='Формат кодирования, байт/фрейм',
        font=('Times New Roman', 11)
        )
    record_sampwidth_label.grid(
        row=3,
        column=0,
        sticky=tkinter.W
        )
    # Создание и размещение радиокнопок выбора формата кодирования.
    record_sampwidth_radiobutton_flag = tkinter.IntVar()
    record_sampwidth_radiobutton_flag.set(2)
    record_sampwidth_radiobutton_1 = tkinter.Radiobutton(
        voice_record_menu_window,
        text='2', 
        font=('Times New Roman', 11), 
        variable=record_sampwidth_radiobutton_flag, 
        value=2
        )
    record_sampwidth_radiobutton_2 = tkinter.Radiobutton(
        voice_record_menu_window, 
        text='4', 
        font=('Times New Roman', 11), 
        variable=record_sampwidth_radiobutton_flag, 
        value=4
        )
    record_sampwidth_radiobutton_1.grid(
        row=4,
        column=0, 
        sticky=tkinter.W
        )
    record_sampwidth_radiobutton_2.grid(
        row=5,
        column=0, 
        sticky=tkinter.W
        )
    # Создание и размещение метки числа каналов.
    record_nchannels_label = tkinter.Label(
        voice_record_menu_window, 
        text='Число каналов',
        font=('Times New Roman', 11)
        )
    record_nchannels_label.grid(
        row=6,
        column=0, 
        sticky=tkinter.W
        )
    # Создание и размещение радиокнопок выбора числа каналов.
    record_nchannels_radiobutton_flag = tkinter.IntVar()
    record_nchannels_radiobutton_flag.set(1)
    record_nchannels_radiobutton_1 = tkinter.Radiobutton(
        voice_record_menu_window, 
        text='Моно', 
        font=('Times New Roman', 11), 
        variable=record_nchannels_radiobutton_flag, 
        value=1
        )
    record_nchannels_radiobutton_2 = tkinter.Radiobutton(
        voice_record_menu_window, 
        text='Стерео', 
        font=('Times New Roman', 11), 
        variable=record_nchannels_radiobutton_flag, 
        value=2
        )
    record_nchannels_radiobutton_1.grid(
        row=7,
        column=0, 
        sticky=tkinter.W
        )
    record_nchannels_radiobutton_2.grid(
        row=8,
        column=0, 
        sticky=tkinter.W
        )
    # Создание и размещение метки длительности записи.
    record_time_label = tkinter.Label(
        voice_record_menu_window, 
        text='Продолжительность записи, с', 
        font=('Times New Roman', 11)
        )
    record_time_label.grid(
        row=0,
        column=1, 
        sticky=tkinter.W
        )
    # Создание и размещение 
    # однострочного текстового поля ввода длительности записи.
    record_time_entry = tkinter.Entry(
        voice_record_menu_window, 
        width=20
        )
    record_time_entry.grid(
        row=1,
        column=1, 
        sticky=tkinter.W
        )
    # Создание и размещение метки ввода индекса аудиоустройств.
    device_index_label = tkinter.Label(
        voice_record_menu_window, 
        text='Введите индекс аудиоустройства:', 
        font=('Times New Roman', 11)
        )
    device_index_label.grid(
        row=2,
        column=1, 
        sticky=tkinter.W
        )
    # Создание и размещение 
    # однострочного текстового поля ввода индекса аудиоустройства.
    device_index_entry = tkinter.Entry(
        voice_record_menu_window, 
        width=20
        )
    device_index_entry.grid(
        row=3,
        column=1, 
        sticky=tkinter.W)
    # Создание и размещение
    # кнопки получения списка доступных аудиоустройств.
    button_get_device_index = tkinter.Button(
        voice_record_menu_window, 
        text='Получить список\nдоступных аудиоустройств', 
        bg='#ff8000', 
        command=get_device_index
        )
    button_get_device_index.grid(
        row=4,
        column=1, 
        rowspan=2, 
        sticky=tkinter.W + tkinter.E
        )
    # Создание и размещение кнопки начала записи голоса.
    button_start_record = tkinter.Button(
        voice_record_menu_window, 
        text='Начать запись голоса', 
        bg='#ff8000', 
        command=voice_recorder
        )
    button_start_record.grid(
        row=6,
        column=1, 
        sticky=tkinter.W + tkinter.E
        )
    # Обновление данных об окне меню записи голоса
    # после размещения на нём виджетов.
    voice_record_menu_window.update_idletasks()
    # Получение размеров окна меню записи голоса.
    voice_record_menu_size_str = voice_record_menu_window.geometry()
    voice_record_menu_size_split = voice_record_menu_size_str.split('+')
    voice_record_menu_size_list = voice_record_menu_size_split[0].split('x')
    voice_record_menu_width = int(voice_record_menu_size_list[0])
    voice_record_menu_height = int(voice_record_menu_size_list[1])
    # Размещение окна меню записи голоса в центре монитора.
    voice_record_menu_window.geometry(
        '+{}+{}'.format(
            screen_width // 2 
            - voice_record_menu_width // 2, 
            screen_height // 2 
            - voice_record_menu_height // 2
            )
        )


def generation_function():
    '''Функция генерации помехи 
    (запускается нажатием кнопки button_generation)
    '''
    # Проверка корректности данных, 
    # введённых в текстовые поля графифческого интерфейса.
    try:
        int(fragment_time_entry.get())
    except ValueError:
        tkinter.messagebox.showerror(
            'Ошибка', 
            'В поле длительности базового фрагмента ' 
            + 'введены некорректные данные'
            )
        return

    try:
        int(total_time_entry.get())
    except ValueError:
        tkinter.messagebox.showerror(
            'Ошибка', 
            'В поле продолжительности помехового сигнала ' 
            + 'введены некорректные данные'
            )
        return

    # Очистка буфера хранения объектов класса.
    SpeechLikeSignal.class_object_buffer.clear()
    # Запуск метода класса, 
    # предназначенного для получения входных данных.
    SpeechLikeSignal.interface_function()
    # Запуск метода класса, предназначенного для создания объектов.
    SpeechLikeSignal.create_instance_function()
    # Запуск метода класса для запуска процесса обработки объектов.
    SpeechLikeSignal.start_object_processing()
    # Запуск метода класса, формирующего буфер с выходными данными.
    SpeechLikeSignal.create_output_data()
    # Запуск метода класса, записывающего выходные данные в аудиофайл.
    SpeechLikeSignal.writing_output_file()
    

def add_files_function():
    '''Функция прикрепления аудиофайлов 
    (запускается нажатием кнопки add_files_button)
    '''
    
    def file_ways_buffer_fill_function():
        '''Функция заполнения 
        буфера хранения абсолютных путей к аудиофайлам 
        (запускается нажатием кнопки add_button)
        '''
        # Предварительная очистка 
        # буфера хранения абсолютных путей к аудиофайлам.
        file_ways_buffer.clear()
        # Заполнение буфера хранения абсолютных путей к аудиофайлам.
        for entry in files_ways_entries:
            # Проверка на указание не пустого пути к аудиофайлу.
            if entry.get() == '':
                tkinter.messagebox.showerror(
                    'Ошибка', 
                    'Указаны не все пути к файлам'
                    )
                break
            else:
                file_ways_buffer.append(entry.get())
        # Изменение индикатора прикрепления файлов
        # в случае успешного указания путей.
        if len(file_ways_buffer) != 0:
            files_ways_status_indicator.config(
                text='Файлы готовы',
                bg='#008000'
                )
            files_ways_window.destroy()

    def get_way_function(index):
        '''Функция получения пути к аудиофайлу
        по нажатию кнопок из списка file_ways_buttons 
        (принимает на вход индекс нажатой кнопки)
        '''
        # Предварительная очистка текстовой строки,
        # соответствующей нажатой кнопке.
        files_ways_entries[index].delete(0, tkinter.END)
        # Вставка в текстовую строку абсолютного пути к файлу. 
        files_ways_entries[index].insert(
            0, 
            tkinter.filedialog.askopenfilename()
            )
    # Проверка корректности данных, 
    # введённых в текстовое поле количества файлов.
    try:
        int(files_number_entry.get())
    except ValueError:
        tkinter.messagebox.showerror(
            'Ошибка', 
            'В поле ввода числа файлов введены некорректные данные')
        return
    # Изменение индикатора прикрепления аудиофайлов
    # (на случай повторного нажатия
    # кнопки прикрепления аудиофайлов)
    files_ways_status_indicator.config(
        text='Файлы не прикреплены!', 
        bg='#ff0000'
        ) 
    # Создание диалогового окна для указания пути к аудиофайлу.
    files_ways_window = tkinter.Toplevel()
    files_ways_window.title('Получение данных о файлах')
    # Создание и размещение текстовой поясняющей метки.
    files_ways_lable = tkinter.Label(
        files_ways_window, 
        text='Укажите путь к файлу:', 
        font=('Times New Roman', 12)
        )
    files_ways_lable.grid(
        row=0, 
        column=0, 
        columnspan=2
        )
    # Создание буферов для хранения текстовых полей 
    # и кнопок прикрепления файлов.
    files_ways_entries = []
    file_ways_buttons = []
    # Определение числа прикрепляемых аудиофайлов.
    files_number = int(files_number_entry.get())
    # Создание текстовых полей и кнопок прикрепления аудиофайлов.
    for i in range(files_number):
        # Создание и размещение тектовых строк.
        files_ways_entries.append(
            tkinter.Entry(files_ways_window, width=100)
            )
        files_ways_entries[i].grid(row=i+1, column=0)
        # Создание и размещение кнопок прикрепления файлов
        # (привязка к клику осуществляется
        # с использованием лямбда-функции
        # для передачи в функцию действия
        # информации об индексе нажатой кнопки).
        file_ways_buttons.append(
            tkinter.Button(
                files_ways_window, 
                text='Указать путь', 
                bg='#747474', 
                command=lambda index=i: get_way_function(index)
                )
            )
        file_ways_buttons[i].grid(row=i+1, column=1)                     
    # Создание и размещение
    # кнопки завершения процесса прикрепления файлов.
    add_button = tkinter.Button(
        files_ways_window, 
        text='ПРИКРЕПИТЬ', 
        bg='#747474', 
        command=file_ways_buffer_fill_function
        )
    add_button.grid(
        row=files_number+1,
        column=0,
        columnspan=2)
    # Размещение диалогового окна
    # для указания пути к аудиофайлу в левом верхнем углу экрана.
    files_ways_window.geometry('+0+0')


# Создание основного окна программы.    
root = tkinter.Tk()
root.title('Генератор речеподобных помех')
# Создание и размещение 
# графического фрейма для ввода параметров помехового сигнала.
heading_1 = tkinter.LabelFrame(
    text='Параметры помехового сигнала', 
    font=('Times New Roman', 12)
    )
heading_1.grid(
    row=0,
    column=0, 
    rowspan=3, 
    padx=10, 
    sticky=tkinter.N
    )
# Создание и размещение метки частоты дискретизации.
frame_rate_label = tkinter.Label(
    heading_1, 
    text='Частота дискретизации, Гц', 
    font=('Times New Roman', 11)
    )
frame_rate_label.grid(
    row=0, 
    column=0, 
    sticky=tkinter.W
    )
# Создание и размещение радиокнопок выбора частоты дискретизации.
frame_rate_radiobutton_flag = tkinter.IntVar()
frame_rate_radiobutton_flag.set(22050)
frame_rate_radiobutton_1 = tkinter.Radiobutton(
    heading_1, 
    text='22050', 
    font=('Times New Roman', 11), 
    variable=frame_rate_radiobutton_flag, 
    value=22050
    )
frame_rate_radiobutton_2 = tkinter.Radiobutton(
    heading_1, 
    text='44100', 
    font=('Times New Roman', 11), 
    variable=frame_rate_radiobutton_flag, 
    value=44100
    )
frame_rate_radiobutton_1.grid(
    row=1,
    column=0, 
    sticky=tkinter.W
    )
frame_rate_radiobutton_2.grid(
    row=2,
    column=0, 
    sticky=tkinter.W
    )
# Создание и размещение метки формата кодирования.
sampwidth_label = tkinter.Label(
    heading_1, 
    text='Формат кодирования, байт/фрейм', 
    font=('Times New Roman', 11)
    )
sampwidth_label.grid(
    row=3,
    column=0, 
    sticky=tkinter.W
    )
# Создание и размещение радиокнопок выбора формата кодирования.
sampwidth_radiobutton_flag = tkinter.IntVar()
sampwidth_radiobutton_flag.set(2)
sampwidth_radiobutton_1 = tkinter.Radiobutton(
    heading_1, 
    text='2', 
    font=('Times New Roman', 11), 
    variable=sampwidth_radiobutton_flag, 
    value=2
    )
sampwidth_radiobutton_2 = tkinter.Radiobutton(
    heading_1, 
    text='4', 
    font=('Times New Roman', 11), 
    variable=sampwidth_radiobutton_flag, 
    value=4
    )
sampwidth_radiobutton_1.grid(
    row=4,
    column=0, 
    sticky=tkinter.W
    )
sampwidth_radiobutton_2.grid(
    row=5,
    column=0, 
    sticky=tkinter.W
    )
# Создание и размещение метки числа каналов.
nchannels_label = tkinter.Label(
    heading_1, 
    text='Число каналов',
    font=('Times New Roman', 11)
    )
nchannels_label.grid(
    row=6,
    column=0, 
    sticky=tkinter.W
    )
# Создание и размещение радиокнопок выбора числа каналов.
nchannels_radiobutton_flag = tkinter.IntVar()
nchannels_radiobutton_flag.set(1)
nchannels_radiobutton_1 = tkinter.Radiobutton(
    heading_1, 
    text='Моно', 
    font=('Times New Roman', 11), 
    variable=nchannels_radiobutton_flag, 
    value=1
    )
nchannels_radiobutton_2 = tkinter.Radiobutton(
    heading_1, 
    text='Стерео', 
    font=('Times New Roman', 11), 
    variable=nchannels_radiobutton_flag, 
    value=2
    )
nchannels_radiobutton_1.grid(
    row=7,
    column=0, 
    sticky=tkinter.W
    )
nchannels_radiobutton_2.grid(
    row=8,
    column=0, 
    sticky=tkinter.W
    )
# Создание и размещение метки длительности звукового фрагмента.
fragment_time_label = tkinter.Label(
    heading_1, 
    text='Длительность базового фрагмента, мс',
    font=('Times New Roman', 11)
    )
fragment_time_label.grid(
    row=9,
    column=0, 
    sticky=tkinter.W
    )
# Создание и размещение 
# однострочного текстового поля ввода длительности звукового фрагмента,
# используемого для генерации помехи.
fragment_time_entry = tkinter.Entry(heading_1, width=20)
fragment_time_entry.grid(
    row=10,
    column=0, 
    sticky=tkinter.W
    )
# Создание и размещение метки длительности помехового сигнала.
total_time_label = tkinter.Label(
    heading_1, 
    text='Продолжительность помехового сигнала, с',
    font=('Times New Roman', 11)
    )
total_time_label.grid(
    row=11,
    column=0, 
    sticky=tkinter.W
    )
# Создание и размещение однострочного текстового поля
# ввода длительности помехового сигнала.
total_time_entry = tkinter.Entry(heading_1, width=20)
total_time_entry.grid(
    row=12,
    column=0, 
    sticky=tkinter.W
    )
# Создание и размещение кнопки открытия меню записи голоса.
button_voice_record_menu = tkinter.Button(
    text='Открыть меню\n записи голоса', 
    font=('Times New Roman', 12), 
    bg='#ff8000', 
    width=15, 
    command=voice_record_menu
    )
button_voice_record_menu.grid(
    row=0, 
    column=1, 
    pady=5, 
    sticky=tkinter.W + tkinter.E
    )
# Создание и размещение графического фрейма, 
# содержащего меню генерации помехи.
heading_2 = tkinter.LabelFrame(
    text='Меню генерации помехи', 
    font=('Times New Roman', 12)
    )
heading_2.grid(row=1, column=1)
# Создание и размещение метки определения числа аудиофайлов.
files_number_label = tkinter.Label(
    heading_2, 
    text='Число файлов для генерации',
    font=('Times New Roman', 11)
    )
files_number_label.grid(
    row=0,
    column=0, 
    sticky=tkinter.W
    )
# Создание и размещение однострочного текстового поля 
# ввода числа аудиофайлов.
files_number_entry = tkinter.Entry(heading_2, width=26)
files_number_entry.grid(
    row=1,
    column=0, 
    sticky=tkinter.W
    )
# Создание и размещение кнопки прикрепления аудиофайлов.
add_files_button = tkinter.Button(
    heading_2, 
    text='Прикрепить аудиофайлы...', 
    bg='#747474', 
    command=add_files_function
    )
add_files_button.grid(
    row=2,
    column=0, 
    pady=5, 
    sticky=tkinter.W
    )
# Создание и размещение метки индикатора прикрепления аудиофайлов.
files_ways_status_label = tkinter.Label(
    heading_2, 
    text='Статус прикрепления файлов',
    font=('Times New Roman', 11)
    )
files_ways_status_label.grid(
    row=3,
    column=0, 
    sticky=tkinter.W
    )
# Создание и размещение индикатора прикрепления аудиофайлов.
files_ways_status_indicator = tkinter.Label(
    heading_2, 
    text='Файлы не прикреплены!', 
    bg='#ff0000'
    )
files_ways_status_indicator.grid(
    row=4,
    column=0, 
    sticky=tkinter.W + tkinter.E
    )
# Создание и размещение кнопки генерации помехи.
button_generation = tkinter.Button(
    heading_2, 
    text='Сгенерировать помеху', 
    bg='#747474', 
    command=generation_function
    )
button_generation.grid(
    row=5,
    column=0, 
    pady=5, 
    sticky=tkinter.W + tkinter.E
    )
# Добавление строки справки.
main_menu = tkinter.Menu(root, tearoff=0)
root.config(menu=main_menu)
main_menu.add_command(label='Справка', command=get_help)
# Обновление данных об основном окне после размещения на нём виджетов.
root.update_idletasks()
# Получение размеров основного окна (в пикселях).
root_size_string = root.geometry()
root_size_string_split = root_size_string.split('+')
root_size_list = root_size_string_split[0].split('x')
root_width = int(root_size_list[0])
root_height = int(root_size_list[1])
# Определение размеров монитора компьютера (в пикселях).
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
# Размещение основного окна в центре монитора.
root.geometry(
    '+{}+{}'.format(
        screen_width//2 
        - root_width//2, 
        screen_height//2 
        - root_height//2)
        )
# Запрещение изменения размеров главного окна.
root.resizable(False, False)
# Запуск основного цикла.
root.mainloop()


