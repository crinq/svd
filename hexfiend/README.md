1. install stuff
  - hex fiend >= 2.15 from https://github.com/HexFiend/HexFiend/releases
  - https://github.com/stm32-rs/svdtools

2. generate patched svd files

        cd stm32-rs/svd && ./extract.sh
        svd patch ../devices/<your_cpu>.yaml

3. generate hex fiend binary template

        cd ../../hexfiend
        python3 svd_to_hexfiend.py ../stm32rs/svd/<your_cpu>.svd.patched <your_cpu>.tcl

4. copy to hex fiend binary template folder

        cp <your_cpu>.tcl ~/Library/Application\ Support/com.ridiculousfish.HexFiend/Templates

5. dump stm32 peripheral config

        st-flash --hot-plug read periph.bin 0x40000000 0x40000

6. open periph.bin and activate the template
