# 定义一个全局变量
global_variable = "This is a global variable"

# 第一个类
class MyClass1:
    def print_global_variable(self):
        print(global_variable)

# 第二个类
class MyClass2:
    def modify_global_variable(self, new_value):
        global global_variable
        global_variable = new_value

# 创建类的实例
obj1 = MyClass1()
obj2 = MyClass2()

# 在第一个类中访问全局变量
obj1.print_global_variable()  # 输出: This is a global variable

# 在第二个类中修改全局变量
obj2.modify_global_variable("New global value")

# 再次在第一个类中访问全局变量
obj1.print_global_variable()  # 输出: New global value
