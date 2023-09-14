from src.jobs.manager import ManagerJob


managerJob = ManagerJob()
managerJob.run()


'''
TODO:

- para funcionar com o labview imagino que o modo padrão, no caso de não seleção deva ser o FrameJob
- ter a seleção se irá querer um crop ou não
- em caso de crop, alterar na pipeline o Tamanho do frame, e ter o padrão normalizado no configs de mesmo tamanho que o isp
- em caso de não haver crop, no uso das teclas de crop, mostrar mensagem de crop indisponível
- para diminuir o log no terminal, apenas mostrar no terminal mensagens após um determinado tempo sem mudança, ou de tempos em tempos

TODO: toda a parte de mostrar a imagem para a o usuário ficara na parte de views
'''