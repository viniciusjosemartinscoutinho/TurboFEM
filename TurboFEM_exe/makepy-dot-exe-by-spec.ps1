#  . 'C:\Users\ucfil\Desktop\desktop\codes\all\FEA\V-git\TurboFEM_exe\makepy-dot-exe-by-spec.ps1'
##Start-Process Powershell -ArgumentList "C:\Users\ucfil\Desktop\desktop\codes\all\FEA\V-git\TurboFEM_exe\makepy-dot-exe-by-spec.ps1"
$tic = Get-Date

function Open-ThisTree {

    try {

        # Pasta onde o terminal está atualmente
        $pastaAtual = Get-Location

        # Busca todos os .py na árvore inteira (raiz + subpastas)
        Get-ChildItem -Path $pastaAtual -Filter "*.py" -File -Recurse | ForEach-Object {

            $origem = $_.FullName

            # Não copia arquivos que já estão na pasta raiz atual
            if ($_.DirectoryName -eq $pastaAtual.Path) {
                return
            }

            # Destino inicial na pasta atual
            $destino = Join-Path $pastaAtual $_.Name


            # Evita sobrescrever arquivos existentes
            if (Test-Path $destino) {

                $i = 1

                while ($true) {

                    $novoNome = "$($_.BaseName)_$i$($_.Extension)"
                    $novoDestino = Join-Path $pastaAtual $novoNome

                    if (!(Test-Path $novoDestino)) {
                        $destino = $novoDestino
                        break
                    }

                    $i++
                }
            }


            # Copia mantendo data/permissões
            Copy-Item -Path $origem -Destination $destino

            Write-Host "Copiado: $origem -> $destino"
        }


        return $pastaAtual.Path

    }
    catch {

        Write-Host $_.Exception.Message
        return $null
    }
}

#go to correct path now
cd $PSScriptRoot
cd ..

#clear it
Remove-Item -Recurse -Force .\build

#pyinstaller TurboFEM.spec
$python=  python -c "import sys; print(sys.executable)"
$pyexe = "$python"

try {
    Open-ThisTree
    & $pyexe  -c "from PIL import Image; Image.open('Fast-FEA-Logo.png').save('Fast-FEA-Logo.ico', sizes=[(16,16),(32,32),(48,48),(256,256)])"
    & $pyexe -m PyInstaller TurboFEM.spec
}
catch {
    Write-Host $_
    #
}
finally {
    Open-ThisTree
    & $python -m pip install --user "pyinstaller"
    & $pyexe  -c "from PIL import Image; Image.open('Fast-FEA-Logo.png').save('Fast-FEA-Logo.ico', sizes=[(16,16),(32,32),(48,48),(256,256)])"
    & $pyexe -m PyInstaller TurboFEM.spec
    Write-Host "end"
}
$toc = Get-Date
$tempo = $toc - $tic
Write-Host "time[s]="
$tempo.TotalSeconds #dtf= 2200 s