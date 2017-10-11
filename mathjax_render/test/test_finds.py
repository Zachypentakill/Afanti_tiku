
from afanti_tiku_lib.latex.util import find_latexes, find_mathmls, displaystyle

print(displaystyle(r'$sg\$sd$\(gg\fracg\)\(tg\)$ vb $\[lk\]'))


a = """
sdfggg<math>
<mstyle displaystyle="true">
    <mrow>

      <munderover>
        <mo>&sum;</mo>
        <mrow>
          <mi>i</mi>
          <mo form="infix">=</mo>
          <mn>1</mn>
        </mrow>
        <mi>n</mi>
      </munderover>


        <mfrac>
          <mn>1</mn>
          <mi>n</mi>
        </mfrac>


    </mrow>
</mstyle>
</math>sgag
"""

print(displaystyle(a))
