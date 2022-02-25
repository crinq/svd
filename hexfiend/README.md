1. generate patched svd files

        cd stm32-rs/svd && ./extract.sh
        svd patch ../devices/<your_cpu>.yaml

2. generate hex fiend binary template

        cd ../../hexfiend
        python3 svd_to_hexfiend.py ../stm32rs/svd/<your_cpu>.svd.patched <your_cpu>.tcl

3. copy to hex fiend binary template folder

        cp <your_cpu>.tcl ~/Library/Application\ Support/com.ridiculousfish.HexFiend/Templates

4. dump stm32 peripheral config

        st-flash --hot-plug read periph.bin 0x40000000 0x40000

5. open periph.bin and activate the template