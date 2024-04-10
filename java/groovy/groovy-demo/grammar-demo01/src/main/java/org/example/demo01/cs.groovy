package org.example.demo01

import groovy.transform.CompileStatic
import groovy.transform.ToString
import groovy.transform.TypeChecked
/**
 * @ClassName: cs
 * @Author : xiwen
 * @Date :2023/12/16  15:20
 * @Description: TODO
 * @Version :1.0
 */
name = "Alice"  // 动态变量声明
name = 42
println(name)

def person = new Person()
person.name = "Alice"


println(person.sayHello()) // 输出: Hello, Alice!

def strippedFirstNewline = '''\
line one
line two
line three
'''
println(strippedFirstNewline)


def name = 'Guillaume' // a plain string
def greeting = "Hello ${person.toString()}"
println(greeting)


String[] strList = new String[10]

strList[0] = '10'

println strList

def student = [10: "李四",20:"王五"]
student.entrySet().forEach {it->println(it)}
for (final def s in student ) {
    println s
}
println student

assert 'a'
assert !''
def nonEmpty = 'a'
assert "$nonEmpty"
def empty = ''
assert !"$empty"

class Color{
    String name
    boolean asBoolean(){
        name == 'green'
    }
}
assert new Color(name: 'green')
assert !new Color(name: 'red')

String concat(String a, String b) {
    a+b
}
assert concat(1 as String, 2 as String) == 12 as String



public concat2(a,b) {
    a+b
}
assert concat2('foo','bar') == 'foobar'
assert concat2(1,2) == 3


class Person2 {
    String firstName
    String lastName
}
def p = new Person2(firstName: 'Raymond', lastName: 'Devos')

p.metaClass.getFormattedName = { "$delegate.firstName $delegate.lastName" }

println p.formattedName


p.metaClass.getFormattedName = { "$delegate.firstName $delegate.lastName" }

println p.formattedName

@TypeChecked()
class Calculator {
    int sum(int x, int y) { x+y }
}

class Person3 {
    String firstName
    String lastName
}
Person3 classic = new Person3(firstName:  'Ada',lastName:  'Lovelace')



class Top {}
class Bottom1 extends Top {}
class Bottom2 extends Top {}

class Computer {
    int compute(String str) {
        str.length()
    }
    String compute(int x) {
        String.valueOf(x)
    }
}

@CompileStatic
void test() {
    def computer = new Computer()
    computer.with {
        assert compute(compute('foobar')) =='6'
    }
}
Computer.metaClass.compute = { String str -> new Date() }
test()


/*float f1 = 0.0f
float f2 = -0.0f
Float f3 = 0.0f
Float f4 = -0.0f

assert f1 == f2
assert ((Float)f1).equalsIgnoreZeroSign((Float) f2)

assert f3 != f4
assert (float) f3 == (float) f4

assert !f1.equals(f2)
assert !f3.equals(f4)

assert f1.equalsIgnoreZeroSign(f2)
assert f3.equalsIgnoreZeroSign(f4)*/





def list1 = ['a', 'b', 'c']
//construct a new list, seeded with the same items as in list1
def list2 = new ArrayList<String>(list1)

assert list2 == list1 // == checks that each corresponding element is the same

// clone() can also be called
def list3 = list1.clone()
assert list3 == list1


def list = [5, 6, 7, 8]
assert list.size() == 4
assert list.getClass() == ArrayList     // the specific kind of list being used

assert list[2] == 7                     // indexing starts at 0
assert list.getAt(2) == 7               // equivalent method to subscript operator []
assert list.get(2) == 7                 // alternative method

list[2] = 9
assert list == [5, 6, 9, 8,]           // trailing comma OK

list.putAt(2, 10)                       // equivalent method to [] when value being changed
assert list == [5, 6, 10, 8]
assert list.set(2, 11) == 10            // alternative method that returns old value
assert list == [5, 6, 11, 8]


assert [1, 2, 3]*.multiply(2) ==
        [1, 2, 3].collect { it.multiply(2) }

list.clear()
list = [0]
// it is possible to give `collect` the list which collects the elements
assert [1, 2, 3].collect(list) { it * 2 } == [0, 2, 4, 6]
assert list == [0, 2, 4, 6]






assert ['a', 'b', 'c', 'd', 'e'].sum{ ((char) it) - ((char) 'a') } == 10
assert ['a', 'b', 'c', 'd', 'e'].sum() == 'abcde'
assert [['a', 'b'], ['c', 'd']].sum() == ['a', 'b', 'c', 'd']
Comparator cl = { a, b -> a==b?0 : (a>b?1:-1)}


list.clear()
list = [0, 2,7, 4, 6]

assert list.max() == 7

list = [null]
if(list){
    def size = list.size()
    println '''cs'''
}

def map = [demo01: 1,demo02:'c']

map.eachWithIndex {key,value,i ->
    println("name $key age: $value index: $i")
}

def remove = map.remove("demo01")
println "demo01 -> " + remove
println map

println map["demo02"]
def key = 'some key'

map = [:]
def gstringKey = "${key.toUpperCase()}"
map.put(gstringKey,'value')
assert map.get('SOME KEY') == null

map = [1:'a', 2:'b', 3:'c']

def entries = map.entrySet()
entries.each { entry ->
    assert entry.key in [1,2,3]
    assert entry.value in ['a','b','c']
}

def keys = map.keySet()
assert keys == [1,2,3] as Set


def people = [
        1: [name:'Bob', age: 32, gender: 'M'],
        2: [name:'Johnny', age: 36, gender: 'M'],
        3: [name:'Claire', age: 21, gender: 'F'],
        4: [name:'Amy', age: 54, gender:'F']
]

def bob = people.find { it.value.name == 'Bob' } // find a single entry
def females = people.findAll { it.value.gender == 'F' }

// both return entries, but you can use collect to retrieve the ages for example
def ageOfBob = bob.value.age
def agesOfFemales = females.collect {
    it.value.age
}

people = [
        1: [name:'Bob', age: 32, gender: 'M'],
        2: [name:'Johnny', age: 36, gender: 'M'],
        3: [name:'Claire', age: 21, gender: 'F'],
        4: [name:'Amy', age: 54, gender:'F']
]
people.findAll {}


String[] vowels = ['a', 'e', 'i', 'o', 'u']
var result = ''
vowels.each {
    result += it
}
assert result == 'aeiou'
result = ''
vowels.eachWithIndex { v, i ->
    result += v * i         // index starts from 0
}
assert result == 'eiiooouuuu'


class Foo {
    static def $static_methodMissing(String name, Object args) {
        return "Missing static method name is $name"
    }
}

assert Foo.bar() == 'Missing static method name is bar'


@ToString
class Person4 {
    String firstName
    String lastName
}



def p4 = new Person4(firstName: 'Jack', lastName: 'Nicholson')
assert p4.toString() == 'org.example.demo01.Person4(Jack, Nicholson)'
println(p4.toString())