public class Homework4 {
	public static void main(String[] args){
		/**
		1. 定义两个int类型变量a1和a2,分别赋值10,11,判断变量是否为偶数,拼接输出结果
		2. 定义两个int类型变量a3和a4,分别赋值12,13,判断变量是否为奇数,拼接输出结果
		*/
		
		//1.
		int a1 = 10;
		int a2 = 11;
		System.out.println(a1 + "是否为偶数:" + (a1 % 2 == 0));
		System.out.println(a2 + "是否为偶数:" + (a2 % 2 == 0));

		int a3 = 12;
		int a4 = 13;
		System.out.println(a1 + "是否为奇数:" + (a3 % 2 != 0));
		System.out.println(a2 + "是否为奇数:" + (a4 % 2 != 0));
		
	}
}