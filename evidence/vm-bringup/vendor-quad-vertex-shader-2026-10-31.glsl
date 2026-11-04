attribute vec4 position;
                                                                    attribute vec4 texCoords;
                                                                    varying vec2 outTexCoords;
                                                                    void main()
                                                                    {
                                                                        gl_Position = position;
                                                                        outTexCoords = texCoords.xy;
                                                                    }
