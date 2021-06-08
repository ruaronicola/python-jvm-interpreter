class Hello {
	int field1;
	int getFieldVal() { return field1; } 
	public static void main(String args[]) {
		System.err.println("Hello World!"); 
		Hello obj = new Hello();
		obj.field1 = 7;
		int i = obj.getFieldVal();
	} 
}
