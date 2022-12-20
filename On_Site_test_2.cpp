#include <iostream>
#include <string>
#include <sstream>
#include <fstream>
#include <vector>
#include <map>
#include<stack>
#include<iomanip>
#include<algorithm>
using namespace std;
class SIC_Line
{
public:
	string Address_label;
	string Op_code;
	string Operant;
	SIC_Line(string line)
	{
		stringstream ss;
		ss << line;
		getline(ss, Address_label, '\t');
		getline(ss, Op_code, '\t');
		getline(ss, Operant, '\t');
	}
};
class SIC_MACRO
{
public:
	string unique_Labels = "AA";
	vector<string> ARGTAB;
	vector<string> KEYWORDTAB;//自創
	vector<SIC_Line> Lines;
	void init_Macro()//回傳巨集行數
	{
		vector<string> parameters;//&開頭為參數名稱
		string p;
		stringstream ss; ss << Lines[0].Operant;
		while (getline(ss, p, ','))
		{
			stringstream ss2; ss2 << p;
			string p2;
			getline(ss2, p2, '=');
			KEYWORDTAB.push_back(p2);//儲存參數名稱
			getline(ss2, p2);
			ARGTAB.push_back(p2);//若有等號 儲存另一端的預設參數
		}
		for (int i=0;i<KEYWORDTAB.size();i++)//取代每個&參數為? 未完成->拼接
		{
			string restring = "?" + to_string(i);
			for (int o = 1; o < Lines.size(); o++)
			{	
				int findIndex = Lines[o].Operant.find(KEYWORDTAB[i]);
				//若該欄字串完全吻合 或是部分字串吻合且下一個字元不為字母 E.G X'&EOR'為真 &EORCK為假
				if ((Lines[o].Operant == KEYWORDTAB[i])||findIndex != -1 && ((findIndex + KEYWORDTAB[i].length())==Lines[o].Operant.length()||!isalpha(Lines[o].Operant[findIndex + KEYWORDTAB[i].length()]))) Lines[o].Operant.replace(Lines[o].Operant.find(KEYWORDTAB[i]), KEYWORDTAB[i].length(), restring);
			}
		}
		
	}
	void extend_Macro(vector<SIC_Line>& target,string head_Address_Label, string operant,map<string,SIC_MACRO> macromap)
	{
		vector<string> args;
		map<string, string> IF_keyword;
		stringstream ss;
		string s;
		ss << operant;
		vector<string> build_Parameters;//處理參數 keyword/無keyword兩種
		while (getline(ss, s, ','))build_Parameters.push_back(s);//使用,拆分字串
		for (auto& L : ARGTAB)args.push_back(L);//複製預設參數
		if (build_Parameters[0].find("=") == -1)//如果沒有=則為依序填入
		{
			for (int i = 0; i < build_Parameters.size(); i++)args[i] = build_Parameters[i];
		}
		else//否則依照關鍵字填入
		{
			for (auto& p : build_Parameters)
			{
				stringstream ss; ss << p;
				string keyword;
				getline(ss, keyword, '=');
				keyword = "&" + keyword;
				auto loc= find(KEYWORDTAB.begin(), KEYWORDTAB.end(), keyword);
				int index = loc - KEYWORDTAB.begin();
				getline(ss, args[index]);
			}
		}
		ofstream ARGTAB("ARGTAB.txt", ios::out);//輸出ARGTAB 沒錯 在這裡 他叫用一次巨集輸出一個 除非他說要生成多個ARGTAB不然我都讓他被覆蓋掉
		for (auto arg : args)ARGTAB << arg << endl;
		ARGTAB.close();

			//TODO IF判斷式
		Lines[1].Address_label = head_Address_Label;//替換首行的address_label
		bool if_skipping = false;//當此flag被標記為true跳過輸出直到else或endif
		bool else_outputting = false;//當此flag標記為true則輸出直到endif
		stack<string> IF_statment;

		bool first = true;//紀錄是否為首行(避免IF判斷式)
		for (int Lcount=1; Lcount < Lines.size()-1; Lcount++)
		{
			SIC_Line L(Lines[Lcount]);
			if (L.Op_code == "SET")continue;
			if (L.Op_code == "IF")continue;
			if (L.Op_code == "ELSE")continue;
			if (L.Op_code == "ENDIF")continue;
			//取代? 最大支援到?9 我是沒心力寫下去了
			if (L.Operant.find("?") != -1)
			{
				int replaceIndex = L.Operant.find("?");
				int keywordIndex = L.Operant[replaceIndex + 1] - '0';
				L.Operant.replace(replaceIndex, 2, args[keywordIndex]);
			}
			//流水號
			if (L.Address_label[0] == '$')
				L.Address_label = "$" + unique_Labels + L.Address_label.substr(1, L.Address_label.length() - 1);
			if (L.Operant[0] == '$')L.Operant = "$" + unique_Labels + L.Operant.substr(1, L.Operant.length() - 1);

			if (first)
			{
				L.Address_label = head_Address_Label;
				first = false;
			}
			if (macromap.find(L.Op_code) != macromap.end())
			{
				L.Address_label = "." + L.Address_label;
				target.push_back(L);
				macromap[L.Op_code].extend_Macro(target, L.Address_label, L.Operant, macromap);
			}
			else target.push_back(L);
		}
		//TOFO:SET IF ELSE WHILE ARRAY
		next_Unique_Labels();//切換至下一個流水號
	}
	void next_Unique_Labels()
	{
		unique_Labels[1]++;
		if (unique_Labels[1] > 'Z')
		{
			unique_Labels[0]++;
			unique_Labels[1] = 'A';
		}
	}
};

class SIC_Program
{
public:
	vector<SIC_Line> Lines;
	vector<SIC_Line> output_Lines;
	map<string, SIC_MACRO> Macros;
	void addline(string line)
	{
		Lines.push_back(SIC_Line(line));
	}
	void print()
	{
		ofstream output("output.txt", ios::out);
		for (auto L : output_Lines)output << L.Address_label << "\t" << L.Op_code << "\t" << L.Operant << endl;
		output.close();
	}
	void pass()
	{
		ofstream DEFTAB("DEFTAB.txt", ios::out);
		ofstream NAMTAB("NAMTAB.txt", ios::out);
		int DEFLine = 0;
		stack<string> target_Macro;
		for (auto& Line : Lines)
		{
			if (Line.Op_code == "MACRO")
			{
				target_Macro.push(Line.Address_label);//將目標MACRO放入堆疊
				vector<string> parameters;
				Macros[Line.Address_label] = SIC_MACRO();
				Macros[target_Macro.top()].Lines.push_back(Line);//輸入首行
			}
			else if (Line.Op_code == "MEND")
			{
				Macros[target_Macro.top()].Lines.push_back(Line);//輸入尾行
				Macros[target_Macro.top()].init_Macro();
				NAMTAB << target_Macro.top() << "," << DEFLine << ",";
				DEFLine += Macros[target_Macro.top()].Lines.size();
				for (auto L : Macros[target_Macro.top()].Lines)DEFTAB << L.Op_code << "\t" << L.Operant << endl;
				NAMTAB << DEFLine - 2 << endl;
				target_Macro.pop();
			}
			else if (Macros.find(Line.Op_code) != Macros.end() && target_Macro.empty())//若不在巨集建立模式(堆疊為空)則展開巨集
			{
				output_Lines.push_back(Line);
				output_Lines.back().Address_label = "." + output_Lines.back().Address_label;
				Macros[Line.Op_code].extend_Macro(output_Lines, Line.Address_label, Line.Operant,Macros);
			}
			else
			{
				if (target_Macro.empty())output_Lines.push_back(Line);
				else Macros[target_Macro.top()].Lines.push_back(Line);
			}
		}
		DEFTAB.close();
		NAMTAB.close();
	}
};

int main()
{
	ifstream input_file("input01.txt", ios::in); 
	string s;
	SIC_Program sic_Program;
	while (getline(input_file,s))
	{
		sic_Program.addline(s);
	}
	input_file.close();
	sic_Program.pass();
	sic_Program.print();
	return 0;
}


