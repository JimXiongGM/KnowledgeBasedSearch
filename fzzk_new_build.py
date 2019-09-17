class InterfaceBuild:
    def __init__(self, writefilename, writetype, strbit):
        """
        :param writefilename: 写入哪个文件名
        :param writetype: 写入方式，'a+'/'w='
        :param strbit: 一个长度为9的数字串，各个为代表是否进行某种处理
        """
        self.writefilename = writefilename
        self.writetype = writetype
        self.strbit = strbit

    def sql_manipulation(self, sqlstr):
        """
        :param sqlstr: 需要进行处理的sql字段串
        :return: 处理后的sql字段串
        """
        # 去HTML标签处理
        if self.strbit[0] == '1':
            dr = re.compile(r'<[^>]+>', re.S)
            sqlstr = dr.sub('', sqlstr)

        # 去特殊字符处理，只保留中文、英文、数字字符
        if self.strbit[1] == '1':
            sqlstr = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "", sqlstr)

        # 去换行符"\n"
        if self.strbit[2] == '1':
            sqlstr = sqlstr.replace('\n', '')

        # 去空格" "
        if self.strbit[3] == '1':
            sqlstr = sqlstr.replace(' ', '')

        # 去转义符"\"
        if self.strbit[4] == '1':
            sqlstr = sqlstr.replace('\\', '_')

        # 去单引号"\'"
        if self.strbit[5] == '1':
            sqlstr = sqlstr.replace('\'', '')

        # 去双引号"\""
        if self.strbit[6] == '1':
            sqlstr = sqlstr.replace('\"', '')

        # 去特殊字符串"nbsp"（第二步去不掉的）
        if self.strbit[7] == '1':
            sqlstr = sqlstr.replace('nbsp', '')

        if self.strbit[8] == '1':
            sqlstr = sqlstr[:20]

        # 去符号"/"
        if self.strbit[9] == '1':
            sqlstr = sqlstr.replace('/', '')

        return sqlstr

    def save_nt(self, line):
        with open(self.writefilename, self.writetype, encoding='utf-8') as f:
            f.write(line)

    def import_case(self):
        sql_text = "select ID,NAME,FILING_NUMBER,APPROVED_DATE,CASE_SOURCE,ILLEGAL_FACTS,ILLEGAL_EVIDENCE,ILLEGAL_EVIDENCE_TYPE,ILLEGAL_DESCRIPT,COMPANY_NAME,CITIZEN_NAME from tbl_case_common_basic"
        newcur = py2sql.mysql_connect(sql_text)
        cursor = newcur.select_result()

        source_dic = {1: "现场检查", 2: "投诉", 3: "举报", 4: "上级机关交办", 5: "其他机关移送", 6: "媒体曝光", 7: "其他", 8: "未知"}

        row = cursor.fetchone()
        i = 1

        while row:
            case_id ="case_" + str(row[0])
            rdf_type = "<" + case_id + "> " + "<Type> " + "\"Administrative_case\".\n"
            na = self.sql_manipulation(str(row[1]))
            if na == "":
                na = self.sql_manipulation(str(row[9]))
                if na == "":
                    na = self.sql_manipulation(str(row[10]))
            name = "<" + case_id + "> " + "<pp:name> " + "\"" + na + "\".\n"
            # case_number = ""
            # if row[2] is not None and str(row[2]) != ' ':
            #     nu = self.sql_manipulation(str(row[2]))
            #     case_number = "<" + case_id + "> " + "<pp:case_number> " + "\"" + nu + "\".\n"
            # approve_time = ""
            # if row[3] is not None and str(row[3]) != ' ':
            #     atime = self.sql_manipulation(str(row[3]))
            #     approve_time = "<" + case_id + "> " + "<pp:approve_time> " + "\"" + atime + "\".\n"
            # case_source = ""
            # if row[4] is not None and str(row[4]) != ' ':
            #     so = self.sql_manipulation(str(row[4]))
            #     case_source = "<" + case_id + "> " + "<pp:case_source> " + "\"" + source_dic[int(so)] + "\".\n"

            # fact = ""
            # if row[5] is not None and str(row[5]) != ' ':
            #     fact = self.sql_manipulation(str(row[5]))
            #     fact = "<" + case_id + "> " + "<pp:fact> " + "\"" + fact + "\".\n"
            # evidence = ""
            # if row[6] is not None and str(row[6]) != ' ':
            #     evidence = self.sql_manipulation(str(row[6]))
            #     evidence = "<" + case_id + "> " + "<pp:evidence> " + "\"" + evidence + "\".\n"
            #
            # evidence_type = ""
            # if row[7] is not None and str(row[7]) != ' ':
            #     ety = self.sql_manipulation(str(row[7]))
            #     evidence_type = "<" + case_id + "> " + "<pp:evidence_type> " + "\"" + ety + "\".\n"
            # evidence_detail = ""
            # if row[8] is not None and str(row[8]) != ' ':
            #     detail = self.sql_manipulation(str(row[8]))
            #     evidence_detail = "<" + case_id + "> " + "<pp:evidence_detail> " + "\"" + detail + "\".\n"

            # rdfi = rdf_type + name + case_number + approve_time + case_source + fact + evidence + evidence_type + evidence_detail
            rdfi = rdf_type + name
            self.save_nt(rdfi)

            row = cursor.fetchone()
            # print(i)
            i += 1
        cursor.close()

    def import_casepunish(self):
        sql_text = "select ID,IS_WARN,IS_FINE,FINE_SUM,IS_REVOKE_LICENSE,IS_ORDER_CLOSURE,IS_DTAIN,DTAIN_DAYS," \
                   "IS_TD_LICENSE,IS_CONFISCATE,CONFISCATE_MONEY,IS_CONFIS_PROPERTY,CONFISCATE_DETAIL,CONFISCATE_PRO_MON," \
                   "IS_FORCE,IS_LIMIT_FREE,IS_DISTRESS,IS_DTAIN_PROPERTY,IS_FRESS,IS_ORTHER_FORCE,IS_HEARING " \
                   "from tbl_case_common_basic"
        newcur = py2sql.mysql_connect(sql_text)
        cursor = newcur.select_result()

        row = cursor.fetchone()
        i = 1
        while row:
            case_id = "case_" + str(row[0])
            content = ""
            if row[1] is not None:
                if row[1] == 1:
                    content += "警告；"
            if row[2] is not None and row[3] is not None:
                if row[2] == 1:
                    content += "罚款："
                    content += str(row[3]) + "；"
            if row[4] is not None:
                if row[4] == 1:
                    content += "吊销许可证或营业执照；"
            if row[5] is not None:
                if row[5] == 1:
                    content += "责令停产停业；"
            if row[6] is not None and row[7] is not None:
                if row[6] == 1:
                    content += "行政拘留："
                    content += str(row[7]) + "；"
            if row[8] is not None:
                if row[8] == 1:
                    content += "暂扣许可证或营业执照；"
            if row[9] is not None and row[10] is not None:
                if row[9] == 1:
                    content += "没收违法所得："
                    content += str(row[10]) + "；"
            if row[11] is not None and row[12] is not None and row[13] is not None:
                if row[11] == 1:
                    content += "没收非法财物；"
                    co = self.sql_manipulation(str(row[12]))
                    content += co + str(row[13]) + "；"
            if row[14] is not None:
                if row[14] == 1:
                    content += "实施行政强制措施；"
            if row[15] is not None:
                if row[15] == 1:
                    content += "限制公民人身自由；"
            if row[16] is not None:
                if row[16] == 1:
                    content += "查封场所、设施或者财物；"
            if row[17] is not None:
                if row[17] == 1:
                    content += "扣押财物；"
            if row[18] is not None:
                if row[18] == 1:
                    content += "冻结存款、汇款；"
            if row[19] is not None:
                if row[19] == 1:
                    content += "其他行政强制措施；"
            if row[20] is not None:
                if row[20] == 1:
                    content += "进行听证；"
            con = self.sql_manipulation(str(content))
            content = "<" + case_id + "> " + "<pp:punish_content> " + "\"" + con + "\".\n"
            rdfi = content
            self.save_nt(rdfi)

            row = cursor.fetchone()
            i += 1

    def import_punish(self):
        sql_text = "select CASE_ID,CONTENT from tbl_case_common_punish"
        newcur = py2sql.mysql_connect(sql_text)
        cursor = newcur.select_result()

        row = cursor.fetchone()
        i = 1
        while row:
            case_id = "case_" + str(row[0])
            # rdf_type = "<" + case_id + "> " + "<Type> " + "\"Administrative_case\".\n"
            content = ""
            if row[1] is not None and str(row[1]) != ' ':
                con = self.sql_manipulation(str(row[1]))
                content = "<" + case_id + "> " + "<pp:punish_content> " + "\"" + con + "\".\n"
            # rdfi = rdf_type + content
            rdfi = content
            self.save_nt(rdfi)

            row = cursor.fetchone()
            # print(i)
            i += 1
        cursor.close()

    def import_company(self):
        sql_text = "select ORGANIZATION_CODE,COMPANY_NAME,ADDRESS,PRINCIPAL,PARTY_TYPE from tbl_case_common_basic where PARTY_TYPE=2 AND ORGANIZATION_CODE IS NOT NULL AND ORGANIZATION_CODE !=' '"
        newcur = py2sql.mysql_connect(sql_text)
        cursor = newcur.select_result()

        row = cursor.fetchone()
        i = 1

        while row:
            if len(str(row[0]).strip())==15 or len(str(row[0]).strip())==18:
                cid = self.sql_manipulation(str(row[0]))
                company_id ="company_" + cid
                rdf_type = "<" + company_id + "> " + "<Type> " + "\"Company\".\n"
                # p_type = "<" + company_id + "> " + "<pp:ptype> " + "\"2\".\n"
                name = ""
                if row[1] is not None and str(row[1]) != ' ':
                    na = self.sql_manipulation(str(row[1]))
                    name = "<" + company_id + "> " + "<pp:name> " + "\"" + na + "\".\n"
                address = ""
                # if row[2] is not None and str(row[2]) != ' ':
                #     ad = self.sql_manipulation(str(row[2]))
                #     address = "<" + company_id + "> " + "<pp:address> " + "\"" + ad + "\".\n"
                principal = ""
                # if row[3] is not None and str(row[3]) != ' ':
                #     pr = self.sql_manipulation(str(row[3]))
                #     principal = "<" + company_id + "> " + "<pp:principal> " + "\"" + pr + "\".\n"

                rdfi = rdf_type + name + address + principal
                self.save_nt(rdfi)

            row = cursor.fetchone()
            # print(i)
            i += 1
        cursor.close()

    def import_law(self):
        sql_text = "select ID,NAME,TIMELINESS,SUBMITLAW_LEVEL,WORD,ORGAN,PROMULGATION,IMPLEMENTATION from tbl_basic_law"
        newcur = py2sql.mysql_connect(sql_text)
        cursor = newcur.select_result()

        row = cursor.fetchone()

        while row:
            idlaw = 'law_' + str(row[0])
            rdf_type = "<" + idlaw + "> " + "<Type> " + "\"Law\".\n"
            name = ""
            if row[1] is not None and str(row[1]) != ' ':
                name = self.sql_manipulation(row[1])
                name = "<" + idlaw + "> " + "<pp:name> " + "\"" + name + "\".\n"
            # if row[2] is not None and str(row[2]) != ' ':
            #     tp = self.sql_manipulation(row[2])
            #     typelaw = "<" + idlaw + "> " + "<pp:timeliness> " + "\"" + tp + "\".\n"
            submitlaw_level = ""
            if row[3] is not None and str(row[3]) != ' ':
                submitlaw_level = self.sql_manipulation(row[3])
                submitlaw_level = "<" + idlaw + "> " + "<pp:submitlaw_level> " + "\"" + submitlaw_level + "\".\n"
            word = ""
            # if row[4] is not None and str(row[4]) != ' ':
            #     word = self.sql_manipulation(str(row[4]))
            #     word = "<" + idlaw + "> " + "<pp:word> " + "\"" + word + "\".\n"
            organ = ""
            # if row[5] is not None and str(row[5]) != ' ':
            #     organ = self.sql_manipulation(str(row[5]))
            #     organ = "<" + idlaw + "> " + "<pp:organ> " + "\"" + organ + "\".\n"
            PROMULGATION = ""
            # if row[6] is not None and str(row[6]) != ' ':
            #     PROMULGATION = self.sql_manipulation(str(row[6]))
            #     PROMULGATION = "<" + idlaw + "> " + "<pp:promulgation> " + "\"" + PROMULGATION + "\".\n"
            IMPLEMENTATION = ""
            # if row[7] is not None and str(row[7]) != ' ':
            #     IMPLEMENTATION = self.sql_manipulation(str(row[7]))
            #     IMPLEMENTATION = "<" + idlaw + "> " + "<pp:implementation> " + "\"" + IMPLEMENTATION + "\".\n"

            rdfi = rdf_type + name + submitlaw_level + word + organ + PROMULGATION + IMPLEMENTATION
            self.save_nt(rdfi)
            # print(idlaw)
            row = cursor.fetchone()
        cursor.close()

    def import_lawitem(self):
        # minID=11279140, maxID=99999999, countID=2310218
        # 单条插入写法
        # step = 11279140
        # while step < 99999999:
        sql_text = "select ID,SERIES,CHAPTER,SECTION,STRIP,FUND,ITEM,CONTENT,LAW_ID from tbl_basic_law_detail"
        newcur = py2sql.mysql_connect(sql_text)
        cursor = newcur.select_result()
        row = cursor.fetchone()
        while row:
            idlawitem = 'lawitem_' + str(row[0])
            rdf_type = "<" + idlawitem + "> " + "<Type> " + "\"Law_item\".\n"
            SERIES = ""
            # if row[1] is not None and row[1] != '':
            #     SERIES = self.sql_manipulation(str(row[1]))
            #     SERIES = "<" + idlawitem + "> " + "<pp:series> " + "\"" + SERIES + "\".\n"
            chapter = ""
            # if row[2] is not None and row[2] != '':
            #     ch = self.sql_manipulation(str(row[2]))
            #     chapter = "<" + idlawitem + "> " + "<pp:chapter> " + "\"" + ch + "\".\n"
            section = ""
            # if row[3] is not None and row[3] != '':
            #     se = self.sql_manipulation(str(row[3]))
            #     section = "<" + idlawitem + "> " + "<pp:section> " + "\"" + se + "\".\n"
            STRIP = ""
            # if row[4] is not None and row[4] != '':
            #     st = self.sql_manipulation(str(row[4]))
            #     STRIP = "<" + idlawitem + "> " + "<pp:strip> " + "\"" + st + "\".\n"
            fund = ""
            # if row[5] is not None and row[5] != '':
            #     fu = self.sql_manipulation(str(row[5]))
            #     fund = "<" + idlawitem + "> " + "<pp:fund> " + "\"" + fu + "\".\n"
            item = ""
            # if row[6] is not None and row[6] != '':
            #     it = self.sql_manipulation(str(row[6]))
            #     item = "<" + idlawitem + "> " + "<pp:item> " + "\"" + it + "\".\n"
            content = self.sql_manipulation(str(row[7]))
            content = "<" + idlawitem + "> " + "<pp:name> " + "\"" + content + "\".\n"
            # rdf_rl = "<" + "law_" + str(row[8]) + "> " + "<rl:law_lawitem> " + "<" + idlawitem + ">.\n"
            rdfi = str(rdf_type) + SERIES + chapter + section + STRIP + fund + item + content
            self.save_nt(rdfi)
            row = cursor.fetchone()

    def import_subject(self):
        sql_text = "select ID,SUB_NAME from tbl_basic_subject"
        newcur = py2sql.mysql_connect(sql_text)
        cursor = newcur.select_result()

        row = cursor.fetchone()
        i = 1

        while row:
            if row[0] is None:
                row = cursor.fetchone()
                continue
            subject_id = "subject_" + str(row[0])
            rdf_type = "<" + subject_id + "> " + "<Type> " + "\"Subject\".\n"
            na = self.sql_manipulation(str(row[1]))
            name = "<" + subject_id + "> " + "<pp:name> " + "\"" + na + "\".\n"

            rdfi = rdf_type + name
            self.save_nt(rdfi)

            row = cursor.fetchone()
            # print(i)
            i += 1
        cursor.close()

    def import_person(self):
        sql_text = "select ID, CITIZEN_NAME, CITIZEN_SEX, CITIZEN_CARD_TYPE, CITIZEN_CARD_CODE, CITIZEN_ADDRESS, PARTY_TYPE from tbl_case_common_basic WHERE PARTY_TYPE=1 AND CITIZEN_CARD_CODE IS NOT NULL AND CITIZEN_CARD_CODE != ' ' AND CITIZEN_CARD_CODE != '/' AND CITIZEN_CARD_TYPE is not NULL"
        newcur = py2sql.mysql_connect(sql_text)
        cursor = newcur.select_result()

        # sex_dic = {1: "男", 2: "女"}
        # card_type_dic = {" 0": "0", "01": "身份证", "02": "驾驶证", "03": "护照", "04": "港澳居民居住证",
        #                  "05": "台湾居民居住证", "06": "统一社会信用代码", "07": "军官证（士兵证）", "10": "其他"}
        row = cursor.fetchone()
        i = 1

        while row:
            ty = self.sql_manipulation(str(row[3]))
            cc = self.sql_manipulation(str(row[4]))
            if cc == '_':
                row = cursor.fetchone()
                continue
            person_id = "person_" + ty + "_" + cc
            # col = cursor.description
            rdf_type = "<" + person_id + "> " + "<Type> " + "\"Person\".\n"
            # p_type = "<" + person_id + "> " + "<pp:ptype> " + "\"1\".\n"
            name = ""
            if row[1] is not None and str(row[1]) != ' ':
                na = self.sql_manipulation(str(row[1]))
                name = "<" + person_id + "> " + "<pp:name> " + "\"" + na + "\".\n"
            sex = ""
            # if row[2] is not None and str(row[2]) != ' ':
            #     se = self.sql_manipulation(str(row[2]))
            #     sex = "<" + person_id + "> " + "<pp:sex> " + "\"" + se + "\".\n"
            card_type = ""
            # if row[3] is not None and str(row[3]) != ' ':
            #     ct = self.sql_manipulation(str(row[3]))
            #     card_type = "<" + person_id + "> " + "<pp:card_type> " + "\"" + ct + "\".\n"
            card_code = ""
            # if row[4] is not None and str(row[4]) != ' ':
            #     cc = self.sql_manipulation(str(row[4]))
            #     card_code = "<" + person_id + "> " + "<pp:card_code> " + "\"" + cc + "\".\n"
            address = ""
            # if row[5] is not None and str(row[5]) != ' ':
            #     ad = self.sql_manipulation(str(row[5]))
            #     address = "<" + person_id + "> " + "<pp:address> " + "\"" + ad + "\".\n"

            rdfi = rdf_type + name + sex + card_type + card_code + address
            self.save_nt(rdfi)

            row = cursor.fetchone()
            # print(i)
            i += 1
        cursor.close()

    def import_power(self):
        sql_text = "select POWER_ID,POWER_CODE,POWER_NAME from tbl_case_common_power"
        newcur = py2sql.mysql_connect(sql_text)
        cursor = newcur.select_result()

        row = cursor.fetchone()
        i = 1

        while row:
            power_id = "power_" + str(row[0])
            rdf_type = "<" + power_id + "> " + "<Type> " + "\"Power\".\n"
            code = ""
            # if row[1] is not None and str(row[1]) != ' ':
            #     co = self.sql_manipulation(str(row[1]))
            #     code = "<" + power_id + "> " + "<pp:code> " + "\"" + co + "\".\n"
            name = ""
            if row[2] is not None and str(row[2]) != ' ':
                na = self.sql_manipulation(str(row[2]))
                name = "<" + power_id + "> " + "<pp:name> " + "\"" + na + "\".\n"

            rdfi = rdf_type + code + name
            self.save_nt(rdfi)

            row = cursor.fetchone()
            # print(i)
            i += 1
        cursor.close()

    def import_staff(self):
        sql_text = "select IDENTITY_ID,OFFICE_NAME,CARD_CODE from tbl_case_common_staff"
        newcur = py2sql.mysql_connect(sql_text)
        cursor = newcur.select_result()

        row = cursor.fetchone()
        i = 1
        while row:
            if row[0] is None:
                row = cursor.fetchone()
                continue
            staff_id = "staff_" + str(row[0])
            rdf_type = "<" + staff_id + "> " + "<Type> " + "\"Staff\".\n"
            name = ""
            if row[1] is not None and str(row[1]) != ' ':
                na = self.sql_manipulation(str(row[1]))
                name = "<" + staff_id + "> " + "<pp:name> " + "\"" + na + "\".\n"
            card_code = ""
            # if row[2] is not None and str(row[2]) != ' ':
            #     cc = self.sql_manipulation(row[2])
            #     card_code = "<" + staff_id + "> " + "<pp:card_code> " + "\"" + cc + "\".\n"

            rdfi = rdf_type + card_code + name
            self.save_nt(rdfi)

            row = cursor.fetchone()
            # print(i)
            i += 1
        cursor.close()

    # 监督机构
    def import_institution(self):
        sql_text = "select ID,NAME from tbl_basic_institution"
        newcur = py2sql.mysql_connect(sql_text)
        cursor = newcur.select_result()

        row = cursor.fetchone()
        i = 1
        while row:
            if row[0] is None:
                row = cursor.fetchone()
                continue
            institution_id = "institution_" + str(row[0])
            rdf_type = "<" + institution_id + "> " + "<Type> " + "\"Institution\".\n"
            name = ""
            if row[1] is not None and str(row[1]) != ' ':
                na = self.sql_manipulation(str(row[1]))
                name = "<" + institution_id + "> " + "<pp:name> " + "\"" + na + "\".\n"

            rdfi = rdf_type + name
            self.save_nt(rdfi)

            row = cursor.fetchone()
            # print(i)
            i += 1
        cursor.close()

    # 执法部门
    def import_organization(self):
        sql_text = "select ID,NAME,FAX,PHONE,ADDRESS from tbl_system_organization"
        newcur = py2sql.mysql_connect(sql_text)
        cursor = newcur.select_result()

        row = cursor.fetchone()
        i = 1
        while row:
            if row[0] is None:
                row = cursor.fetchone()
                continue
            organization_id = "organization_" + str(row[0])
            rdf_type = "<" + organization_id + "> " + "<Type> " + "\"Organization\".\n"
            name = ""
            if row[1] is not None and str(row[1]) != ' ':
                na = self.sql_manipulation(str(row[1]))
                name = "<" + organization_id + "> " + "<pp:name> " + "\"" + na + "\".\n"
            fax = ""
            # if row[2] is not None and str(row[2]) != ' ':
            #     fa = self.sql_manipulation(str(row[2]))
            #     fax = "<" + organization_id + "> " + "<pp:fax> " + "\"" + fa + "\".\n"
            phone = ""
            # if row[3] is not None and str(row[3]) != ' ':
            #     ph = self.sql_manipulation(str(row[3]))
            #     phone = "<" + organization_id + "> " + "<pp:phone> " + "\"" + ph + "\".\n"
            address = ""
            # if row[4] is not None and str(row[4]) != ' ':
            #     ad = self.sql_manipulation(str(row[4]))
            #     address = "<" + organization_id + "> " + "<pp:address> " + "\"" + ad + "\".\n"

            rdfi = rdf_type + name + fax + phone + address
            self.save_nt(rdfi)

            row = cursor.fetchone()
            # print(i)
            i += 1
        cursor.close()

    def relation_case_company(self):
        # sql_text = "select ID from tbl_case_common_basic"
        sql_text = "select ID,ORGANIZATION_CODE,PARTY_TYPE from tbl_case_common_basic where PARTY_TYPE=2 AND ORGANIZATION_CODE IS NOT NULL AND ORGANIZATION_CODE !=' '"
        newcur = py2sql.mysql_connect(sql_text)
        cursor = newcur.select_result()

        row = cursor.fetchone()
        i = 1
        while row:
            if len(str(row[1]).strip())==15 or len(str(row[1]).strip())==18:
                cid = self.sql_manipulation(str(row[1]))
                company_id ="company_" + cid
                case_id = "case_" + str(row[0])
                rdf_type = "<" + case_id + "> " + "<rl:case_company> " + "<" + company_id + ">.\n"

                rdfi = rdf_type
                self.save_nt(rdfi)

            row = cursor.fetchone()
            # print(i)
            i += 1
        cursor.close()

    def relation_case_subject(self):
        sql_text = "select ID,SUBJECT_ID from tbl_case_common_basic"
        newcur = py2sql.mysql_connect(sql_text)
        cursor = newcur.select_result()

        row = cursor.fetchone()
        i = 1
        while row:
            case_id = "case_" + str(row[0])
            subject_id = "subject_" + str(row[1])
            rdf_type = "<" + case_id + "> " + "<rl:case_subject> " + "<" + subject_id + ">.\n"

            rdfi = rdf_type
            self.save_nt(rdfi)

            row = cursor.fetchone()
            # print(i)
            i += 1
        cursor.close()

    def relation_case_person(self):
        # sql_text = "select ID from tbl_case_common_basic"
        sql_text = "select ID, CITIZEN_CARD_TYPE, CITIZEN_CARD_CODE, PARTY_TYPE from tbl_case_common_basic WHERE PARTY_TYPE=1 AND CITIZEN_CARD_CODE IS NOT NULL AND CITIZEN_CARD_CODE != ' ' AND CITIZEN_CARD_CODE != '/' AND CITIZEN_CARD_TYPE is not NULL"
        newcur = py2sql.mysql_connect(sql_text)
        cursor = newcur.select_result()

        row = cursor.fetchone()
        i = 1
        while row:
            case_id = "case_" + str(row[0])
            ty = self.sql_manipulation(str(row[1]))
            cc = self.sql_manipulation(str(row[2]))
            if cc == '_':
                row = cursor.fetchone()
                continue
            person_id = "person_" + ty + "_" + cc
            rdf_type = "<" + case_id + "> " + "<rl:case_person> " + "<" + person_id + ">.\n"

            rdfi = rdf_type
            self.save_nt(rdfi)

            row = cursor.fetchone()
            # print(i)
            i += 1
        cursor.close()

    def relation_case_power(self):
        sql_text = "select CASE_ID,POWER_ID from tbl_case_common_power"
        newcur = py2sql.mysql_connect(sql_text)
        cursor = newcur.select_result()

        row = cursor.fetchone()
        i = 1
        while row:
            case_id = "case_" + str(row[0])
            power_id = "power_" + str(row[1])
            rdf_type = "<" + case_id + "> " + "<rl:case_power> " + "<" + power_id + ">.\n"

            rdfi = rdf_type
            self.save_nt(rdfi)

            row = cursor.fetchone()
            # print(i)
            i += 1
        cursor.close()

    def relation_power_lawitem(self):
        sql_text = "select POWER_ID,LAW_DETAIL_ID from tbl_basic_gist"
        newcur = py2sql.mysql_connect(sql_text)
        cursor = newcur.select_result()

        row = cursor.fetchone()
        i = 1
        while row:
            power_id = "power_" + str(row[0])
            lawitem_id = "lawitem_" + str(row[1])
            rdf_type = "<" + power_id + "> " + "<rl:power_lawitem> " + "<" + lawitem_id + ">.\n"

            rdfi = rdf_type
            self.save_nt(rdfi)

            row = cursor.fetchone()
            # print(i)
            i += 1
        cursor.close()

    def relation_power_subject(self):
        sql_text = "select SUBJECT_ID,POWER_ID from tbl_basic_subject_power"
        newcur = py2sql.mysql_connect(sql_text)
        cursor = newcur.select_result()

        row = cursor.fetchone()
        i = 1
        while row:
            power_id = "power_" + str(row[1])
            subject_id = "=subject_" + str(row[0])
            rdf_type = "<" + power_id + "> " + "<rl:power_subject> " + "<" + subject_id + ">.\n"

            rdfi = rdf_type
            self.save_nt(rdfi)

            row = cursor.fetchone()
            # print(i)
            i += 1
        cursor.close()

    def relation_case_staff_subject(self):
        sql_text = "select CASE_ID, IDENTITY_ID, SUBJECT_ID from tbl_case_common_staff"
        newcur = py2sql.mysql_connect(sql_text)
        cursor = newcur.select_result()

        row = cursor.fetchone()
        i = 1
        while row:
            if row[1] is None:
                row = cursor.fetchone()
                continue
            case_id = "case_" + str(row[0])
            staff_id = "staff_" + str(row[1])
            subject_id = "subject_" + str(row[2])
            rdf_type1 = "<" + case_id + "> " + "<rl:case_staff> " + "<" + staff_id + ">.\n"
            rdf_type2 = "<" + subject_id + "> " + "<rl:subject_staff> " + "<" + staff_id + ">.\n"

            rdfi = rdf_type1 + rdf_type2
            self.save_nt(rdfi)

            row = cursor.fetchone()
            # print(i)
            i += 1
        cursor.close()

    def relation_law_lawitem(self):
        # minID=11279140, maxID=99999999, countID=2310218
        sql_text = "select ID,LAW_ID from tbl_basic_law_detail"
        newcur = py2sql.mysql_connect(sql_text)
        cursor = newcur.select_result()
        row = cursor.fetchone()
        while row:
            lawitem_id = "lawitem_" + str(row[0])
            law_id = "law_" + str(row[1])
            rdf_type = "<" + law_id + "> " + "<rl:law_lawitem> " + "<" + lawitem_id + ">.\n"

            rdfi = rdf_type
            self.save_nt(rdfi)

            row = cursor.fetchone()

    def relation_case_lawitem(self):
        i = 0
        sql_caseid = "select CASE_ID,GIST_ID from tbl_case_common_gist"
        curcaseid = py2sql.mysql_connect(sql_caseid)
        cursor1 = curcaseid.select_result()
        rowcaseid = cursor1.fetchone()
        while rowcaseid:
            cid =str(rowcaseid[0]).replace(" ", "")
            case_id = "case_" + cid
            gist_id = str(rowcaseid[1])

            sql_lawitemid = "select LAW_DETAIL_ID from tbl_basic_gist where ID='%s'" % gist_id
            curlawitemid = py2sql.mysql_connect(sql_lawitemid)
            cursor2 = curlawitemid.select_result()
            rowlawitemid = cursor2.fetchone()

            while rowlawitemid:
                lid = str(rowlawitemid[0]).replace(" ", "")
                lawitem_id = "lawitem_" + lid
                if case_id is not None and lawitem_id is not None:
                    rdf_type = "<" + case_id + "> " + "<rl:case_lawitem> " + "<" + lawitem_id + ">.\n"
                    rdfi = rdf_type
                    self.save_nt(rdfi)

                rowlawitemid = cursor2.fetchone()
            cursor2.close()

            rowcaseid = cursor1.fetchone()
            
            with open("i.txt", 'w', encoding='utf-8') as f:
                f.write(str(i))
            i += 1
        cursor1.close()

    # 执法部门-执法主体
    def relation_organization_subject(self):
        sql_text = "select ORGANIZATION_ID,SUBJECT_ID from tbl_basic_organization_subject"
        newcur = py2sql.mysql_connect(sql_text)
        cursor = newcur.select_result()
        row = cursor.fetchone()
        while row:
            organization_id = "organization_" + str(row[0])
            subject_id = "subject_" + str(row[1])
            rdf_type = "<" + organization_id + "> " + "<rl:organization_subject> " + "<" + subject_id + ">.\n"

            rdfi = rdf_type
            self.save_nt(rdfi)

            row = cursor.fetchone()

    # 监督机构-执法部门
    def relation_institution_organization(self):
        sql_text = "select ID,ORGANIZATION_ID from tbl_basic_institution"
        newcur = py2sql.mysql_connect(sql_text)
        cursor = newcur.select_result()
        row = cursor.fetchone()
        while row:
            institution_id = "institution_" + str(row[0])
            organization_id = "organization_" + str(row[1])
            rdf_type = "<" + institution_id + "> " + "<rl:institution_organization> " + "<" + organization_id + ">.\n"

            rdfi = rdf_type
            self.save_nt(rdfi)

            row = cursor.fetchone()


if __name__ == '__main__':
    filename = 'relation_case_lawitem.nt'
    w_type = 'a+'
    bit = '1111111111'
    handler = InterfaceBuild(filename, w_type, bit)

#     handler.import_case()
#     print("finish 1")
#     # handler.import_punish()
#     # print("finish 2")
#     # handler.import_casepunish()
#     # print("finish 2")
#     handler.import_company()
#     print("finish 3")
#     handler.import_law()
#     print("finish 4")
#     handler.import_lawitem()
#     print("finish 5")
#     handler.import_subject()
#     print("finish 6")
#     handler.import_person()
#     print("finish 7")
#     handler.import_power()
#     print("finish 8")
#     handler.import_staff()
#     print("finish 9")
#     handler.import_institution()
#     print("finish 10")
#     handler.import_organization()
#     print("finish 11")
#     print("finish part one")

#     handler.relation_case_company()
#     print("finish 1")
#     handler.relation_case_subject()
#     print("finish 2")
#     handler.relation_case_person()
#     print("finish 3")
#     handler.relation_case_power()
#     print("finish 4")
#     handler.relation_power_lawitem()
#     print("finish 5")
#     handler.relation_power_subject()
#     print("finish 6")
#     handler.relation_case_staff_subject()
#     print("finish 7")
#     handler.relation_law_lawitem()
#     print("finish 8")
    handler.relation_case_lawitem()
    print("finish 9")
#     handler.relation_organization_subject()
#     print("finish 10")
#     handler.relation_institution_organization()
#     print("finish 11")
#     print("finish")
