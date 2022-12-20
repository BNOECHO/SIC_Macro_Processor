class SIC_Line:
    def __init__(self, line: str):
        self.Address_label, self.Op_code, self.Operant = line.split('\t')

class SIC_MACRO:
    unique_Labels = "AA"
    ARGTAB = []
    KEYWORDTAB = []
    Lines = []
    
    def init_Macro(self, DEFoutput):
        parameters = []
        p = ""
        ss = ""
        for line in self.Lines:
            ss += line.Operant
        while ',' in ss:
            p, ss = ss.split(',', 1)
            ss2 = ""
            for s in p:
                ss2 += s
            p2 = ""
            if '=' in ss2:
                p2, _ = ss2.split('=', 1)
                self.KEYWORDTAB.append(p2)
                p2, _ = ss2.split('=')
                self.ARGTAB.append(p2)
            else:
                self.KEYWORDTAB.append(ss2)
                self.ARGTAB.append("")
        for i in range(len(self.KEYWORDTAB)):
            restring = "?" + str(i)
            for o in range(1, len(self.Lines)):
                findIndex = self.Lines[o].Operant.find(self.KEYWORDTAB[i])
                if self.Lines[o].Operant == self.KEYWORDTAB[i] or (findIndex != -1 and ((findIndex + len(self.KEYWORDTAB[i])) == len(self.Lines[o].Operant) or not self.Lines[o].Operant[findIndex + len(self.KEYWORDTAB[i])].isalpha())):
                    self.Lines[o].Operant.replace(self.Lines[o].Operant.find(self.KEYWORDTAB[i]), len(self.KEYWORDTAB[i]), restring)
        for L in self.Lines:
            DEFoutput.write(L.Op_code + "\t" + L.Operant + "\n")
        return len(self.Lines)

    def extend_Macro(self, target, head_Address_Label, operant, macromap):
        args = []
        IF_keyword = {}
        ss = ""
        for s in operant:
            ss += s
        build_Parameters = []
        while ',' in ss:
            p, ss = ss.split(',', 1)
            build_Parameters.append(p)
        build_Parameters.append(ss)
        for i in range(len(build_Parameters)):
            if build_Parameters[i] in self.KEYWORDTAB:
                IF_keyword[self.KEYWORDTAB[i]] = build_Parameters[i]
                args.append(self.ARGTAB[i])
            else:
                args.append(build_Parameters[i])
        for i in range(1, len(self.Lines)):
            if self.Lines[i].Op_code != "ENDM":
                line = self.Lines[i].Op_code + "\t" + self.Lines[i].Operant
                for j in range(len(args)):
                    line = line.replace("?" + str(j), args[j])
                for j in range(len(self.KEYWORDTAB)):
                    if self.KEYWORDTAB[j] in IF_keyword:
                        line = line.replace(self.ARGTAB[j], IF_keyword[self.KEYWORDTAB[j]])
                target.append(SIC_Line(head_Address_Label + "\t" + line))
                head_Address_Label = ""
            else:
                return
        return

def process_Macro(target, macromap, startline):
    while True:
        if target[startline].Op_code in macromap:
            macromap[target[startline].Op_code].extend_Macro(target, target[startline].Address_label, target[startline].Operant, macromap)
            target.pop(startline)
        elif target[startline].Op_code == "END":
            return
        else:
            startline += 1
def main():
    filepath = input("Enter file path: ")
    with open(filepath, 'r') as f:
        lines = f.readlines()
    DEFoutput = open("DEF.txt", "w")
    target = []
    macromap = {}
    for line in lines:
        sl = SIC_Line(line.strip())
        if sl.Op_code == "MACRO":
            macro = SIC_MACRO()
            while sl.Op_code != "MEND":
                macro.Lines.append(sl)
                # sl = SIC_Line(next(lines).strip())
                sl = SIC_Line(line.strip())
            macro.Lines.append(sl)
            macromap[macro.Lines[0].Address_label] = macro
            macro.init_Macro(DEFoutput)
        else:
            target.append(sl)
    DEFoutput.close()
    process_Macro(target, macromap, 0)

if __name__ == "__main__":
    main()
