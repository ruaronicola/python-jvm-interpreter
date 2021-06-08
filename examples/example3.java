class test {
	int field1 = 2;
	void testme() {}
	public static void main (String a[]){
		test tobj = new test();
		int i = tobj.field1;
		tobj.field1 = 7;
	}
}
