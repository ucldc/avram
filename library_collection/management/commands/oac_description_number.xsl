<xsl:stylesheet
  version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  >
 
  <!-- xslt for

 ucldc/registry - load description and collection number into registry
 input such as: http://www.oac.cdlib.org/search?raw=1&identifier=ark:/13030/tf1b69n716

  -->


  <xsl:variable name="smallcase" select="'abcdefghijklmnopqrstuvwxyz'" />
  <xsl:variable name="uppercase" select="'ABCDEFGHIJKLMNOPQRSTUVWXYZ'" />

  <xsl:template match="crossQueryResult">
    <xsl:apply-templates select="facet[@field='oac4-tab']/group[1]/docHit[1]/meta[1]"/>
  </xsl:template>
 
  <xsl:template match="meta">
    <xsl:variable name="number">
      <xsl:value-of select="normalize-space(identifier[starts-with(translate(text(), $uppercase, $smallcase),'collection number:')])"/>
    </xsl:variable>
    <collection>
      <xsl:attribute name="number">
        <xsl:value-of select="substring($number, 20, string-length($number))"/>
      </xsl:attribute>
      <xsl:value-of select="description[@q='abstract']"/>
    </collection>
  </xsl:template>
 
</xsl:stylesheet>
