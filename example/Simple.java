class Simple {
	static int field1;
	int ifield;
	static void foo(Simple obj, int param){
		obj.ifield = 10;
		obj.bar();
	}
	static int bar(){
		return 1;
	}
	public static void main(String args[]) {
		int i = args.length;
		int j = 1000027;
		int k = Simple.field1;

		Simple s = new Simple();
		Simple.foo(s, j);
	} 
}

