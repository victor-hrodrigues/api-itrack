import cx_Oracle
import csv
from pandas import DataFrame
import sys
import hashlib

# cx_Oracle.init_oracle_client(lib_dir=r"C:\Program Files\Oracle\instantclient_19_10")
# cx_Oracle.init_oracle_client(lib_dir=r"/Users/elisandroboeno/oracle/instantclient_19_8")

uid = "rastreamento" # usuário
pwd = "rastreamento" # senha
db = "(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=172.17.50.250)(PORT=1521)))(CONNECT_DATA=(SERVER=DEDICATED)(SERVICE_NAME=orcl)))"

class Db ():
    def __init__(self):
        try:
            self.con = cx_Oracle.connect(uid+"/"+pwd+"@"+db)  # cria a conexão
            print("Connection ORACLE established")
            self.con.autocommit = True
            self.cursor = self.con.cursor()  # cria um cursor
        except cx_Oracle.DatabaseError as error:
            print(error)

    def __dictify(self, row, cur):
        fields = [el[0] for el in cur.description]
        obj = {}
        for i, col in enumerate(row):
            obj[fields[i]] = col
        return obj

    def getCur(self):
        return self.cursor

    def __insert(self, sql, args=tuple()):
        try:
            self.cursor.execute(sql, args)
            self.con.commit()
            print("INSERTING/UPDATING...")
            return True
        except Exception as e:
            print("An exception occurred ::", e)
            return False

    def __query(self, sql, args=tuple()):
        self.cursor.execute(sql, args)
        data = DataFrame(self.cursor.fetchall())
        data.columns = [desc[0] for desc in self.cursor.description]
        # data = []
        # for row in self.cursor:
        #     data.append(self.__dictify(row, self.cursor))
        return data

    def hashPassword(self, login, senha):
        arrLogin = list(login)
        arrSenha = list(senha)
        arrSenhaInvertida = arrSenha[::-1]
        lenLogin = len(arrLogin)
        lenSenha = len(arrSenha)
        lenSenhaInvertida = len(arrSenhaInvertida)
        tamanho = 0
        resString = ''

        # Verifica qual das duas strings é a maior
        if (lenLogin > lenSenha):
            tamanho = lenLogin
        else:
            tamanho = lenSenha
        
        # Percorre todos os indices da maior string
        for x in range(tamanho):
            
            if x < lenLogin:
                resString += str(arrLogin[x])
            else:
                resString += str(x)

            if x < lenSenhaInvertida:
                resString += str(arrSenhaInvertida[x])
            else:
                resString += str(x)

        result = hashlib.md5(resString.encode())
        
        return result.hexdigest()


    def getTokenValido(self, token):
        try:
            sql = self.__query("select id_usuario, nome, empresa, login from rastreamento.usuarios where ativo = 'T' and itrack_token = '%s'" % (token))
            return sql
        except Exception as e:
            print("Sql sem Token ::", e) 
            return ''

    def getUsuario(self, login, senha):
        try:
            sql = self.__query("select id_usuario, nome, empresa, login from rastreamento.usuarios where ativo = 'T' and login = :1 and senha = :2 and rownum = 1", (login, senha))
            return sql
        except Exception as e:
            print("Sql sem Usuario ::", e)
            return ''

    def getUsuarioLogin(self, login):
        try:
            sql = self.__query("select id_usuario, nome, empresa, login, email, itrack_codigo_recuperacao from rastreamento.usuarios where ativo = 'T' and login = '%s' and rownum = 1" % (login))
            return sql
        except Exception as e:
            print("Sql sem Usuario Login ::", e)
            return ''
    
    def loginUsuario(self, id, token, device_id):
        try:
            #sql = self.__insert("update rastreamento.usuarios set itrack_token = :2 /*, itrack_token_duration = to_date(:3, 'YYYY-MM-DD HH24:MI:SS')*/ where id_usuario = :1", (id, token))
            sql = self.__insert("update rastreamento.usuarios set itrack_token = '%s', itrack_device_id = '%s' where id_usuario = '%s'" % (token, device_id, id))
            return sql
        except Exception as e:
            print("Update Usuario ::", e)
            return ''

    def logoutUsuario(self, device_id):
        try:
            sql = self.__insert("update rastreamento.usuarios set itrack_token = '', itrack_device_id = '' where itrack_device_id = '%s'" % (device_id))
            return sql
        except Exception as e:
            print("Update Usuario ::", e)
            return ''

    def alteraSenhaUsuario(self, id, nova_senha):
        try:
            sql = self.__insert("update rastreamento.usuarios set senha = '%s' where id_usuario = '%s'" % (nova_senha, id))
            return sql
        except Exception as e:
            print("Update Senha Usuario ::", e)
            return ''

    def enviaEmailRecuperacao(self, email, codigo):
        try:
            sql = self.__insert("insert into rastreamento.emails (email, titulo, mensagem, data_hora) values ('%s', 'AllMob - Recuperação de acesso', 'Código para recuperação de acesso: %s', sysdate)" % (email, codigo))
            return sql
        except Exception as e:
            print("Update Senha Usuario ::", e)
            return ''

    def salvaCodigoRecuperacao(self, id, codigo):
        try:
            sql = self.__insert("update rastreamento.usuarios set itrack_codigo_recuperacao = '%s' where id_usuario = '%s'" % (codigo, id))
            return sql
        except Exception as e:
            print("Update Senha Usuario ::", e)
            return ''

    def getEmpresas(self, empresa):
        try:
            sql = self.__query("SELECT id_empresa id_cliente, nome nome_cliente FROM rastreamento.empresas where ativo = 'T' START WITH id_empresa = %s CONNECT BY PRIOR id_empresa = matriz" % (empresa))
            return sql
        except Exception as e:
            print("Sql sem Usuario ::", e)
            return ''

    def getVeiculos(self, empresa):
        try:
            sql = self.__query("select v.id as id_veiculo, v.placa, v.tipo, eq.serial, e.id_empresa as id_cliente, e.nome as cliente_nome, e.cpf_cnpj, p.id_posicao, to_char(p.data_hora,'YYYYMMDDHH24MISS') data_hora, p.lat, p.lon, CASE WHEN ve.endereco IS NOT NULL THEN '.'||ve.endereco ELSE p.endereco END as endereco, p.velocidade, p.odometro, c.nome as condutor, case when p.pos_chave = 'T' then 1 else 0 end ignicao, p.motivo||' '||p.motivo_complemento as motivo from veiculos v join empresas e on e.id_empresa = v.empresa join equipamentos eq on eq.placa = v.placa and eq.backup = 'F' left join posicoes p on p.placa = v.placa left join condutores c on c.id_condutor = p.condutor LEFT join veiculos_endereco ve on ve.placa = v.placa and ve.data_hora >= p.data_hora-4/1440 where v.ativo = 'T' and v.placa in (SELECT DISTINCT(placa) as placa FROM (SELECT veic.placa FROM veiculos veic WHERE veic.empresa IN (SELECT id_empresa FROM empresas START WITH id_empresa = %s CONNECT BY PRIOR id_empresa = matriz) UNION SELECT esp.placa FROM espelhamento esp WHERE esp.empresa = %s))" % (empresa, empresa))
            return sql
        except Exception as e:
            print("Sql sem Veiculos ::", e)
            return ''

    def getVeiculo(self, veiculo_id):
        try:
            sql = self.__query("select v.id, v.placa, v.tipo, v.empresa, e.id_equipamento, e.serial, e.aparelho, aparelhos.nome as aparelho_nome from veiculos v join equipamentos e on e.placa = v.placa and e.backup = 'F' join aparelhos on aparelhos.id_aparelho = e.aparelho where v.id = %s and rownum = 1" % (veiculo_id))
            return sql
        except Exception as e:
            print("Sql sem Veiculo ::", e)
            return ''

    def getVeiculosFiltro(self, empresa, page, size, q, gps, ign, minVel, semTransmissao):
        try:
            if (q != ''):
                sql = self.__query("select v.id as id_veiculo, v.placa, CASE WHEN v.tipo is not null THEN v.tipo ELSE 0 END tipo, eq.serial, e.id_empresa as id_cliente, e.nome as cliente_nome, e.cpf_cnpj, p.id_posicao, to_char(p.data_hora,'YYYYMMDDHH24MISS') data_hora, p.lat, p.lon, CASE WHEN ve.endereco IS NOT NULL THEN '.'||ve.endereco ELSE p.endereco END as endereco, p.velocidade, p.odometro, c.nome as condutor, case when p.pos_chave = 'T' then 1 else 0 end ignicao, p.motivo||' - '||p.motivo_complemento as motivo from veiculos v join empresas e on e.id_empresa = v.empresa join equipamentos eq on eq.placa = v.placa and eq.backup = 'F' join posicoes p on p.placa = v.placa left join condutores c on c.id_condutor = p.condutor left join veiculos_endereco ve on ve.placa = v.placa and ve.data_hora >= p.data_hora-4/1440 where v.ativo = 'T' and v.placa like upper('%s%s%s') and v.placa in (SELECT DISTINCT(placa) as placa FROM (SELECT veic.placa FROM veiculos veic WHERE veic.empresa IN (SELECT id_empresa FROM empresas START WITH id_empresa = %s CONNECT BY PRIOR id_empresa = matriz) UNION SELECT esp.placa FROM espelhamento esp WHERE esp.empresa = %s)) order by v.placa asc OFFSET %s ROWS FETCH NEXT %s ROWS ONLY" % ('%', q, '%', empresa, empresa, page, size))
            else:
                sql = self.__query("select v.id as id_veiculo, v.placa, CASE WHEN v.tipo is not null THEN v.tipo ELSE 0 END tipo, eq.serial, e.id_empresa as id_cliente, e.nome as cliente_nome, e.cpf_cnpj, p.id_posicao, to_char(p.data_hora,'YYYYMMDDHH24MISS') data_hora, p.lat, p.lon, CASE WHEN ve.endereco IS NOT NULL THEN '.'||ve.endereco ELSE p.endereco END as endereco, p.velocidade, p.odometro, c.nome as condutor, case when p.pos_chave = 'T' then 1 else 0 end ignicao, p.motivo||' - '||p.motivo_complemento as motivo from veiculos v join empresas e on e.id_empresa = v.empresa join equipamentos eq on eq.placa = v.placa and eq.backup = 'F' join posicoes p on p.placa = v.placa left join condutores c on c.id_condutor = p.condutor left join veiculos_endereco ve on ve.placa = v.placa and ve.data_hora >= p.data_hora-4/1440 where v.ativo = 'T' and v.placa in (SELECT DISTINCT(placa) as placa FROM (SELECT veic.placa FROM veiculos veic WHERE veic.empresa IN (SELECT id_empresa FROM empresas START WITH id_empresa = %s CONNECT BY PRIOR id_empresa = matriz) UNION SELECT esp.placa FROM espelhamento esp WHERE esp.empresa = %s)) order by v.placa asc OFFSET %s ROWS FETCH NEXT %s ROWS ONLY" % (empresa, empresa, page, size))
            
            return sql
        except Exception as e:
            print("Sql sem Veiculos Filtro ::", e)
            return ''

    def getPosicoes(self, veiculo_id):
        try:
            sql = self.__query("select p.id_posicao, veiculos.id as id_veiculo, to_char(p.data_hora,'YYYYMMDDHH24MISS') data_hora, p.lat, p.lon, CASE WHEN ve.endereco IS NOT NULL THEN '.'||ve.endereco ELSE p.endereco END as endereco, p.velocidade, p.odometro, c.nome as condutor, case when p.pos_chave = 'T' then 1 else 0 end ignicao, p.motivo, p.motivo_complemento from posicoes p join veiculos on veiculos.placa = p.placa left join condutores c on c.id_condutor = p.condutor LEFT join veiculos_endereco ve on ve.placa = veiculos.placa and ve.data_hora >= p.data_hora-4/1440 where veiculos.id = %s and rownum = 1" % (veiculo_id))
            return sql
        except Exception as e:
            print("Sql sem Posicoes ::", e)
            return ''

    def getPosicoesDia(self, veiculo_id, data_ini, data_fim):
        try:
            sql = self.__query("select p.id_posicao, veiculos.id as id_veiculo, to_char(p.data_hora,'YYYYMMDDHH24MISS') data_hora, p.lat, p.lon, CASE WHEN ve.endereco IS NOT NULL THEN '.'||ve.endereco ELSE p.endereco END as endereco, p.velocidade, p.odometro, c.nome as condutor, case when p.pos_chave = 'T' then 1 else 0 end ignicao, p.motivo||' - '|| p.motivo_complemento as motivo from posicoes_dia p join veiculos on veiculos.placa = p.placa left join condutores c on c.id_condutor = p.condutor LEFT join veiculos_endereco ve on ve.placa = veiculos.placa and ve.data_hora >= p.data_hora-4/1440 where veiculos.id = %s and p.data_hora between to_date('%s','YYYYMMDDHH24MISS') and to_date('%s','YYYYMMDDHH24MISS') order by p.data_hora desc" % (veiculo_id, data_ini, data_fim))
            return sql
        except Exception as e:
            print("Sql sem Posicoes Dia ::", e)
            return ''

    def getPosicoesDiaDataHora(self, veiculo_id, data_hora):
        try:
            sql = self.__query("select p.id_posicao, veiculos.id as id_veiculo, to_char(p.data_hora,'YYYYMMDDHH24MISS') data_hora, p.lat, p.lon, CASE WHEN ve.endereco IS NOT NULL THEN '.'||ve.endereco ELSE p.endereco END as endereco, p.velocidade, p.odometro, p.horimetro, c.nome as condutor, case when p.pos_chave = 'T' then 1 else 0 end ignicao, p.motivo||' '||p.motivo_complemento as motivo, p.bateria_veiculo as bateria, case when p.temperatura1 in (0, 300) then 0 else p.temperatura1 end temperatura1 from posicoes_dia p join veiculos on veiculos.placa = p.placa left join condutores c on c.id_condutor = p.condutor LEFT join veiculos_endereco ve on ve.placa = veiculos.placa and ve.data_hora >= p.data_hora-4/1440 where veiculos.id = %s and to_date(to_char(p.data_hora,'YYYYMMDDHH24MISS'),'YYYYMMDDHH24MISS') = to_date('%s','YYYYMMDDHH24MISS') order by p.data_hora desc" % (veiculo_id, data_hora))
            return sql
        except Exception as e:
            print("Sql sem Posicoes Dia Data Hora ::", e)
            return ''

    def getPosicoesGeo(self, veiculo_id, data_ini, data_fim):
        try:
            sql = self.__query("select p.lat, p.lon from posicoes_dia p join veiculos on veiculos.placa = p.placa left join condutores c on c.id_condutor = p.condutor where veiculos.id = %s and p.data_hora between to_date('%s','YYYYMMDDHH24MISS') and to_date('%s','YYYYMMDDHH24MISS')" % (veiculo_id, data_ini, data_fim))
            return sql
        except Exception as e:
            print("Sql sem Posicoes Geo ::", e)
            return ''

    def getPontosReferencia(self, cliente_id, page, size):
        try:
            sql = self.__query("select id_ponto_referencia, nome, empresa id_cliente, latitude lat, longitude lon, raio from pontos_referencias where empresa = %s order by id_ponto_referencia asc OFFSET %s ROWS FETCH NEXT %s ROWS ONLY" % (cliente_id, page, size))
            return sql
        except Exception as e:
            print("Sql sem Pontos Ref. ::", e)
            return ''

    def getComandos(self, veiculo_id, user_id):
        try:
            sql = self.__query("SELECT eq.funcionalidade AS nome, cmd.id FROM (SELECT equip.aparelho, cfg.campo, cfg.funcionalidade, equip.id_equipamento as equipamento FROM equipamentos_cfg cfg JOIN equipamentos equip ON cfg.equipamento = equip.id_equipamento WHERE cfg.funcionalidade in ('Bloqueio','Sirene') and equip.id_equipamento in (select id_equipamento from equipamentos where placa in (select placa from veiculos where id = %s) and backup = 'F') AND cfg.funcionalidade IS NOT NULL) eq JOIN comandos cmd ON eq.aparelho = cmd.aparelho AND eq.campo = cmd.campo WHERE cmd.mostra = 'T' AND eq.funcionalidade IN (SELECT distinct(nome) FROM (select uf.funcionalidade_nome as nome from usuarios_funcionalidades uf WHERE uf.usuario_id = %s))" % (veiculo_id, user_id))
            return sql
        except Exception as e:
            print("Sql sem Comandos ::", e)
            return ''

    def getComandosParametros(self, comando_id):
        try:
            sql = self.__query("SELECT id, comando, nome, lista_valores FROM comandos_parametros WHERE comando = '%s' OR comando IN ( SELECT id FROM comandos WHERE pai = '%s' )" % (comando_id, comando_id))
            return sql
        except Exception as e:
            print("Sql sem Comandos Parametros ::", e)
            return ''

    def getComandosEnviados(self, veiculo_id, data_ini, data_fim):
        try:
            sql = self.__query("select ce.id, e.placa, veiculos.id id_veiculo, ce.usuario, to_char(ce.data,'DD/MM/YYYY HH24:MI:SS') as data, to_char(ce.data_envio,'DD/MM/YYYY HH24:MI:SS') as data_envio, ce.comando, ecfg.funcionalidade from comandos_enviados ce join comandos c on c.id = ce.comando join equipamentos e on e.id_equipamento = ce.equipamento JOIN equipamentos_cfg ecfg on ecfg.campo = c.campo and e.id_equipamento = ecfg.equipamento join veiculos on veiculos.placa = e.placa where veiculos.id = %s and ce.data between to_date('%s','YYYYMMDDHH24MISS') and to_date('%s','YYYYMMDDHH24MISS')" % (veiculo_id, data_ini, data_fim))
            return sql
        except Exception as e:
            print("Sql sem Comandos Enviados ::", e)
            return ''

    def getComandosEnviadosParametros(self, cmd_id):
        try:
            sql = self.__query("select cp.nome, cep.valor from comandos_enviados_parametros cep join comandos_parametros cp on cp.id = cep.parametro where cep.cmd_enviado = %s" % (cmd_id))
            return sql
        except Exception as e:
            print("Sql sem Comandos Enviados Parametros ::", e)
            return ''

    def getComandoSequence(self):
        try:
            sql = self.__query("select seq_cmd_envio.nextval as id from dual")
            return sql
        except Exception as e:
            print("Insert Comando ::", e)
            return ''

    def gravaComando(self, id, comando, equipamento, serial, usuario, parametro, aparelho, aparelho_nome):
        try:
            sql = self.__insert("INSERT INTO comandos_espera(id, comando, codigo, equipamento, equipamento_serial, usuario, data, parametro, aparelho, aparelho_nome, pai) VALUES ('%s', '%s', (SELECT codigo FROM comandos WHERE id = %s and rownum=1), '%s', '%s', '%s', SYSDATE, '%s', '%s', '%s', '')" % (id, comando, comando, equipamento, serial, usuario, parametro, aparelho, aparelho_nome))
            return sql
        except Exception as e:
            print("Insert Comando ::", e)
            return ''

    def gravaParametros(self, comando_espera, parametro, valor):
        try:
            sql = self.__insert("INSERT INTO comandos_espera_parametros(cmd_espera, parametro, valor) VALUES ('%s', '%s', '%s')" % (comando_espera, parametro, valor))
            return sql
        except Exception as e:
            print("Insert Parametro ::", e)
            return ''

    def getAncoras(self, veiculo_id):
        try:
            sql = self.__query("select id, veiculo_id, raio_ativo, ignicao_ativo, lat, lon, to_char(created_at,'YYYYMMDDHH24MISS') as created_at, created_by, usuarios.nome as nome, usuario_ecriador, usuario_monitorando, raio from ancoras left join usuarios on usuarios.id_usuario = ancoras.created_by where veiculo_id = %s" % (veiculo_id))
            return sql
        except Exception as e:
            print("Lista Ancora ::", e)
            return ''

    def getAncoraId(self, ancora_id):
        try:
            sql = self.__query("select id, veiculo_id, raio_ativo, ignicao_ativo, lat, lon, to_char(created_at,'YYYYMMDDHH24MISS') as created_at, created_by, usuario_ecriador, usuario_monitorando, raio from ancoras where id = %s" % (ancora_id))
            return sql
        except Exception as e:
            print("Lista Ancora ID ::", e)
            return ''

    def getAncoraSequence(self):
        try:
            sql = self.__query("select seq_ancoras.nextval as id from dual")
            return sql
        except Exception as e:
            print("Sequence Ancora ::", e)
            return ''

    def gravaAncora(self, id_ancora, veiculo_id, raio_ativa, ignicao_ativa, lat, lon, usuario):
        try:
            sql = self.__insert("INSERT INTO ancoras(id, veiculo_id, raio_ativo, ignicao_ativo, lat, lon, created_by, raio) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', 100)" % (id_ancora, veiculo_id, raio_ativa, ignicao_ativa, lat, lon, usuario))
            return sql
        except Exception as e:
            print("Insert Ancora ::", e)
            return ''

    def delAncora(self, id_ancora):
        try:
            sql = self.__insert("delete ancoras where id = %s" % (id_ancora))
            return sql
        except Exception as e:
            print("Delete Ancora ::", e)
            return ''
        
    def getViagens(self, veiculo_id, data_ini, data_fim):
        try:
            sql = self.__query("SELECT rownum, ROUND((tempo*100)/NVL(NULLIF(tmpTotal,0), 1)) as percTimeLine, ROUND((tmpTotSit*100)/NVL(NULLIF(tmpTotal,0), 1)) as percSit, tempo/60 tempo, tmpTotSit, tmpTotal, situacao, inicio, fim, condutor, inicio_format, fim_format, saida_de, chegou_em, placa, veiid, CASE WHEN distancia>=0 THEN trim(to_char(distancia, '99999990.09')) ELSE '0.0' END distancia FROM (SELECT tempo, tot tmpTotSit, SUM(distinct(tot)) over (partition by plc) tmpTotal, situacao, trunc(distancia/10, 1) distancia, to_char(NVL(inicio, TRUNC(to_date('%s', 'YYYYMMDDHH24MISS'))), 'HH24:MI') inicio, to_char(fim, 'HH24:MI') fim, plc placa, veiid, NVL(condutor, 'Não Identificado') condutor, to_char(inicio,'YYYYMMDDHH24MISS') as inicio_format, to_char(fim,'YYYYMMDDHH24MISS') as fim_format, saida_de, lead(saida_de) OVER (PARTITION BY plc ORDER BY inicio) chegou_em FROM (SELECT SUM(tempo) OVER (partition by situacao, v.placa) tot ,t.*, v.placa plc, v.id as veiid, LAG(t.endereco) OVER(PARTITION BY v.placa ORDER BY inicio) saida_de FROM veiculos v, table(pkg_relatorio.deslocamento(to_date('%s', 'YYYYMMDDHH24MISS'), to_date('%s', 'YYYYMMDDHH24MISS'), v.id, 10)) t WHERE v.id = %s ) WHERE situacao = 'Movimento' ORDER BY placa, inicio)" % (data_ini, data_ini, data_fim, veiculo_id))
            return sql
        except Exception as e:
            print("Lista vigens ::", e)
            return ''
            
    def dbClose(self):
        print("Connection ORACLE closed")
        self.con.close()
        return
