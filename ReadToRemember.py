# Read to Remember

"""
В системе 3 основных действия:
    1 Добавить новый прочтенный материал: ссылка, текст, документ
    2 Получить список того, что на сегодняшний день нужно повторить
    3 Отметить что повторил
    
Система будет составлять список для повторения на день, согласно кривой обучения
Если одна из задач не будет выполнена, можно корректировать даты повторов,
добавлять и убирать новые повторения. 

Добавить:
    Кнопка "Запомнил"
    Тесты на запомненное
    Градиент того на сколько хорошо запомнил
    Систему фильтров задач
    Система приоритезации
    Система категоризации
    Спец интерфейс для указания глав книг
    Специальная кривая обучения для больших источников, как книга
    Для каждого таска добавить:
        - подразделы для отдельных глав или сегоментов
        - категория материала, область знаний
    Добавить функционал "Помидоро" 25мин чтения, 5 мин отдыха
    Когда нагрзка падает ниже уровня Х, добавить таск "Пора изучить что-нибудь новенькое"
        Можно предложить тему на основе популярности категории или качества запоминания
    В случаях высокой нагрузки сдвигать часть тасков на поздних этапах
    Добавить объем источника:
        - время видео 
        - время затраченное на первое прочтение
        - количество символов / страниц
        - выводить из этого оценку затраченного времени
    
    Таск состоящий из набора флеш-карт
    
        
По собранной статистики выводить персонализированную кривую обучения.

"""
from appJar import gui

study_list = dict()# Содержит библиотеку материалов для запоминания
normal_tasks_for_today = list() # Task_id
overdue_tasks = list() # Task_id
all_tasks = list() # Task_id
meta_file = dict()
# Meta Template
"""
meta:{
      tasks:{task_id:{}},
      update_dttm:''
}
"""

# Task template:
"""
task_id:{
      name:'',
      type:'',
      body:'',
      'priority':'',
      create_dttm:'',
      current_curve_stage:'',
      last_repeat_date:'',
      next_repeat_date:'',
      update_dttm:''
}
"""

params = {
        'lib_path':'',
        'meta_file_path':'',
        'docs_folder':''
        }

learning_curve = {
        # Number of days before need to repeat
        1:0,
        2:1,
        3:7,
        4:28,
        5:84,
        6:336
        }

class Meta():
    """
    Holds methods related to processing metadata
    """
    def add_task(task_body,priority=1):
        global meta_file
        task = Task.create_task(task_body,priority=1)
        if len(meta_file['tasks'].keys()) > 0:
            task_id = meta_file['tasks'].keys()[-1] + 1
        else:
            task_id = 1

        meta_file['tasks'][task_id] = task
        normal_tasks_for_today.append(task_id)
        
    def remove_task(task_id):
        """
        Удалить задачу из списка
        """
        pass
    
    def read_meta():
        global meta_file
        global normal_tasks_for_today
        global overdued_tasks
        global all_tasks
        meta_file = read_file_as_json(params['meta_file_path'])
        
        today = get_date()
        today_dttm = get_dttm()
        
        for task_id, task in meta_file['tasks']:
            lcs = learning_curve[Task['current_curve_stage']] # Learning Curve Stage
            if ((Task['next_repeat_date'] < today and add_days(Task['last_repeat_date'],lcs) == today) 
                or Task.next_repeat_date == today):
                # Делаем сегодня
                Task.next_repeat_date = today
                Task.update_dttm = today_dttm # Вынести в отдельную функцию все апдейты?
                normal_tasks_for_today.append(task_id)
                pass
            elif Task['next_repeat_date'] < today and add_days(Task['last_repeat_date'],lcs) < today:
                # Опоздал, штрафная
                overdue_tasks.append(task_id)
                Task.mark_as_read(task_id)
            else:
                # Время еще не пришло
                pass
            all_tasks.append(task_id)
            
        
        if meta_file == dict():
            return False
        return True

    def get_tasks_for_today():
        """
        Возвращяет Json со всеми тасками на сегодня
        """
        list_of_tasks = dict()
        for nt in normal_tasks_for_today:
            list_of_tasks[nt] = meta_file['tasks'][nt]
    
        for ot in overdued_tasks:
            list_of_tasks[ot] = meta_file['tasks'][ot]
            
        return list_of_tasks
    
    def get_tasks_for_date(next_repeat_date):
        """
        Возвращяет Json со всеми тасками с повторением на определенную дату
        """
        list_of_tasks = dict()
        for t in all_tasks:
            if meta_file['tasks'][t]['next_repeat_date'] == next_repeat_date:
                list_of_tasks[t] = meta_file['tasks'][t]
            
        return list_of_tasks
        
    
    def get_full_list():
        """
        Возвращяет Json со всеми тасками в системе
        Подумать над системой фильтров
        """
        list_of_tasks = dict()
        for t in all_tasks:
            list_of_tasks[t] = meta_file['tasks'][t]
            
        return list_of_tasks

class Task():
    """
    Holds methods related to introducing changes to tasks
    """
    def create_task(task_body,priority=1):
        """
        Добавить задачу в список
        """
        def add_as_text():
            pass
        # def add_as_hyperlink(): - Не уверен, что требуется
            
        def add_as_file():
            pass
        
        today = get_date()
        today_dttm = get_dttm()
        
        task_obj = {
          #'name':'', ?
          'type':'', # Text / File / Link
          'body':'',
          'status':'New',
          'priority':priority,
          'create_dttm':today_dttm,
          'current_curve_stage':1,
          'last_repeat_date':today,
          'next_repeat_date':today,
          'update_dttm':today_dttm
          }
        
        return task_obj
    
    def mark_as_read(task_id):
        """
        Отметить как прочитанное на текущий момент
        """
        global meta_file
        today = get_date()
        today_dttm = get_dttm()
        
        if meta_file.tasks[task_id].current_curve_stage == learning_curve.keys()[-1]:
            meta_file.tasks[task_id].mark_as_complete(task_id)
        else:
            meta_file['tasks'][task_id]['status'] = 'Read'
            meta_file['tasks'][task_id]['current_curve_stage'] += 1
            meta_file['tasks'][task_id]['next_repeat_date'] = today + learning_curve[meta_file.tasks[task_id].current_curve_stage]
            meta_file['tasks'][task_id]['update_dttm'] = today_dttm
            meta_file['tasks'][task_id]['last_repeat_date'] = today
              
        return True
    
    def mark_as_overdue(task_id):
        """
        Отметить как просроченное
        """
        global meta_file
        today_dttm = get_dttm()
        
        meta_file['tasks'][task_id]['status'] = 'Overdue'
        meta_file['tasks'][task_id]['update_dttm'] = today_dttm
              
        return True
    
    def mark_as_complete(task_id):
        """
        Отметить как выполненную задачу, "материал освоен"
        """
        global meta_file
        today = get_date()
        today_dttm = get_dttm()
        
        meta_file['tasks'][task_id]['status'] = 'complete'
        meta_file['tasks'][task_id]['next_repeat_date'] = None
        meta_file['tasks'][task_id]['update_dttm'] = today_dttm
        meta_file['tasks'][task_id]['last_repeat_date'] = today
        return True
    
    def mark_as_canceled(task_id):
        pass

    def delay_task():
        """
        Отложить задачу на заданный промежуток времени 
        ? со смещением кривой ?
        """
        pass

def get_date():
    pass

def get_dttm():
    pass

def add_days(date,days):
    pass

def startup():
    """
    Подготовка данных к работе приложения
    Зачитывание метаданных
    """
    meta_read_successful = Meta.read_meta()
    if not meta_read_successful:
        return False
    
    # Start_UI() - to be added
    
    return True
        
def read_file_as_json(path):
    meta_file = dict()
    meta_file['tasks'] = dict()
    meta_file['update_dttm'] = get_dttm()
    print(meta_file)
    return meta_file
    
def write_file(path,text):
    pass

# Execution
startup()
Meta.add_task('new task')
print(meta_file)

# GUI
def press(button):
    global app
    if button == "Add":
        new_task = app.getEntry("New Task")
        if new_task == '':
            app.popUp("Task is not specified",)
        print("New task:", new_task)
    else:
        pass
    return False

with gui("Study Materials", "400x200", font={'size':18}) as app:
    app.addLabel("title", "Plan for today:")
    app.addLabelEntry("New Task")
    app.addButtons(["Add"], press)



