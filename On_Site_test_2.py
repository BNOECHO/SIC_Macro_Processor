from copy import deepcopy
import sys

class SIC_Line:

    address_Label = str()
    Op_code = str()
    Operant = str()

    def __init__(self, line: str):

        temp_cmd = line.removesuffix('\n').split('\t')
        length = len(temp_cmd)
        if len(temp_cmd) == 1:
            self.address_Label = temp_cmd[0]
            self.Op_code = ""
            self.Operant = ""

        elif len(temp_cmd) == 2:
            self.address_Label = temp_cmd[0]
            self.Op_code = temp_cmd[1]
            self.Operant = ""
        else:
            self.address_Label = temp_cmd[0]
            self.Op_code = temp_cmd[1]
            self.Operant = temp_cmd[2]


class SIC_MACRO:

    unique_Labels = "AA"
    KEYWORDTAB = list()
    ARGTAB = list()
    Lines = list()

    def init_Macro(self):

        p = str()
        ss = self.Lines[0].Operant
        ss2 = ss.split(',')
        for s in ss2:
            self.KEYWORDTAB.append(s.split('=')[0])  # 儲存參數名稱
            self.ARGTAB.append(s.split('=')[1] if len(
                s.split('=')) > 1 else "")  # 若有等號 儲存另一端的預設參數

        for i in range(len(self.KEYWORDTAB)):  # 取代每個&參數為? 未完成->拼接
            restring = "?" + str(i)
            for o in range(1, len(self.Lines)):
                findIndex = self.Lines[o].Operant.find(self.KEYWORDTAB[i])
                if findIndex != -1:
                    print("findIndex")
                # 若該欄字串完全吻合 或是部分字串吻合且下一個字元不為字母 E.G X'&EOR'為真 &EORCK為假
                if self.Lines[o].Operant == self.KEYWORDTAB[i] or (findIndex != -1 and ((findIndex + len(self.KEYWORDTAB[i])) == len(self.Lines[o].Operant) or (not self.Lines[o].Operant[findIndex + len(self.KEYWORDTAB[i])].isalpha()))):
                    self.Lines[o].Operant = self.Lines[o].Operant.replace(
                        self.KEYWORDTAB[i], restring)

    def extend_Macro(self, target, head_Address_Label: str, Operant: str, macromap: dict):
        args = list()
        IF_keyword = dict()
        # 處理參數 keyword/無keyword兩種並使用','拆分字串
        build_Parameters = Operant.split(',')
        args = [L for L in self.ARGTAB]  # 複製預設參數
        if build_Parameters[0].find('=') == -1:  # 如果沒有=則為依序填入
            for i in range(len(build_Parameters)):
                args[i] = build_Parameters[i]
        else:  # 否則依照關鍵字填入
            for p in build_Parameters:
                keyword = "&" + p.split('=')[0]
                index = self.KEYWORDTAB.index(keyword)
                args[index] = p.split('=')[1]
        for arg in args:
            self.ARGTAB.append(arg)

            # TODO IF判斷式
        self.Lines[1].address_Label = head_Address_Label  # 替換首行的address_label
        if_skipping = False  # 當此flag被標記為true跳過輸出直到else或endif
        else_outputting = False  # 當此flag標記為true則輸出直到endif
        IF_statment = list()

        first = True
        for i in range(1, len(self.Lines)-1):
            L = deepcopy(self.Lines[i])
            if L.Op_code in ["SET", "IF", "ELSE", "ENDIF"]:
                continue  # 取代? 最大支援到?9 我是沒心力寫下去了

            if L.Operant.find('?') != -1:
                replaceIndex = L.Operant.find('?')
                keywordIndex = int(L.Operant[replaceIndex + 1])
                # replace the index keywordIndex to the value of args[keywordIndex]
                L.Operant = L.Operant.replace(
                    "?"+str(keywordIndex), args[keywordIndex])
            # 流水號
            if L.address_Label.startswith('$'):
                L.address_Label = L.address_Label.replace(
                    '$', "$" + self.unique_Labels)
            if L.Operant.startswith('$'):
                L.Operant = L.Operant.replace('$', "$" + self.unique_Labels)

            if first:
                L.address_Label = head_Address_Label
                first = False
            if macromap.get(L.Op_code) != None:
                L.address_Label = "." + L.address_Label
                target.append(L)
                macromap[L.Op_code].extend_Macro(
                    target, L.address_Label, L.Operant, macromap)
            else:
                target.append(L)

            # TODO:SET IF ELSE WHILE ARRAY

    def next_Unique_Labels(self):
        # convert self.unique_Labels[0] to char and +1 then convert back to string
        self.unique_Labels = self.unique_Labels[0] + \
            chr(ord(self.unique_Labels[0]) + 1)
        if self.unique_Labels[1] > 'Z':
            self.unique_Labels = chr(ord(self.unique_Labels[0]) + 1) + "A"


class SIC_Program:
    Lines = list()
    output_Lines = list()
    Macros = dict()

    def addline(self, line: SIC_Line):
        self.Lines.append(line)

    def pass_(self):
        DEFTAB = list()
        NAMTAB = list()
        DEFLine = 0
        target_Macro = list()
        for Line in self.Lines:
            if Line.Op_code == "MACRO":
                target_Macro.append(Line.address_Label)  # 將目標MACRO放入堆疊
                self.Macros[Line.address_Label] = SIC_MACRO()
                self.Macros[target_Macro[-1]].Lines.append(Line)  # 輸入首行
            elif Line.Op_code == "MEND":
                self.Macros[target_Macro[-1]].Lines.append(Line)  # 輸入尾行
                self.Macros[target_Macro[-1]].init_Macro()
                NAMTAB.append(target_Macro[-1] + "\t" + str(DEFLine) + ",")
                DEFLine += len(self.Macros[target_Macro[-1]].Lines)
                for L in self.Macros[target_Macro[-1]].Lines:
                    DEFTAB.append(L.Op_code + "\t" + L.Operant + "\n")
                NAMTAB.append(str(DEFLine - 2) + "\n")
                target_Macro.pop()
            # 若不在巨集建立模式(堆疊為空)則展開巨集
            elif self.Macros.get(Line.Op_code) != None and len(target_Macro) == 0:
                self.output_Lines.append(deepcopy(Line))
                self.output_Lines[-1].address_Label = "." + \
                    self.output_Lines[-1].address_Label
                self.Macros[Line.Op_code].extend_Macro(
                    self.output_Lines, Line.address_Label, Line.Operant, self.Macros)
            else:
                if len(target_Macro) == 0:
                    self.output_Lines.append(Line)
                else:
                    self.Macros[target_Macro[-1]].Lines.append(Line)
        with open("DEFTAB.txt", "w") as f:
            for L in DEFTAB:
                f.write(L)
        with open("NAMTAB.txt", "w") as f:
            for L in NAMTAB:
                f.write(L)

    def print(self):
        with open("output.txt", "w") as f:
            for L in self.output_Lines:

                f.write(L.address_Label + "\t" +
                        L.Op_code + "\t" + L.Operant + "\n")


if __name__ == "__main__":
    
    # check python version must be 3.9 or higher
    if (sys.version_info.major != 3 or sys.version_info.minor < 9):
        exit("Python version must be 3.9 or higher")
    
    sic_progrem = SIC_Program()
    with open("input01.txt", "r") as f:
        for line in f:
            if len(line) > 0:  # 避免空行
                sic_progrem.addline(SIC_Line(line))
    sic_progrem.pass_()
    sic_progrem.print()
