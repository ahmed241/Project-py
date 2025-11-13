import { useState, useEffect } from 'react'
export default function AnimatedBG({ children }: { children: React.ReactNode }) {
    const [matrixElements, setMatrixElements] = useState<
        { id: number; value: number; x: number; y: number; delay: number; duration: number }[]
    >([]);

    // Create a generator that runs only on the client after mount
    useEffect(() => {
        const generateMatrixElements = () => {
            return Array.from({ length: 50 }, (_, i) => ({
                id: i,
                value: Math.floor(Math.random() * 100),
                x: Math.random() * 100,
                y: Math.random() * 100,
                delay: Math.random() * 5,
                duration: 8 + Math.random() * 12
            }));
        };

        // small timeout not required; just set after mount
        setMatrixElements(generateMatrixElements());
    }, []); // run once on client

    // similarly, if you used Math.random in other places (like matrix columns),
    // precompute those client-side as well. Example:
    const [matrixColumns, setMatrixColumns] = useState<
        { id: number; left: string; animationDelay: string; animationDuration: string }[]
    >([]);

    useEffect(() => {
        const cols = Array.from({ length: 15 }, (_, i) => {
            // compute client-only random-ish values:
            const left = `${i * 7}%`;
            const animationDelay = `${i * 0.3}s`;
            const animationDuration = `${16 + Math.random() * 4}s`;
            return { id: i, left, animationDelay, animationDuration };
        });
        setMatrixColumns(cols);
    }, []);

    return(
        < div className = "absolute inset-0 z-0" >
            {/* Base gradient */ }
            < div className = "absolute inset-0 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 animate-gradient-shift" />

                {/* Animated grid */ }
                < div className = "absolute inset-0 opacity-20" >
                    <div className="animated-grid" />
                </div >

        {/* Floating mathematical elements */ }
        < div className = "absolute inset-0 overflow-hidden" >
        {
            matrixElements.map((elem) => (
                <div
                    key={elem.id}
                    className="absolute text-purple-400/30 font-mono text-xl font-bold floating-element"
                    style={{
                        left: `${elem.x}%`,
                        top: `${elem.y}%`,
                        animationDelay: `${elem.delay}s`,
                        animationDuration: `${elem.duration}s`
                    }}
                >
                    {elem.value}
                </div>
            ))
        }
                </div >

        {/* Animated shapes */ }
        < div className = "absolute inset-0 overflow-hidden opacity-10" >
                  <div className="rotating-shape shape-1" />
                  <div className="rotating-shape shape-2" />
                  <div className="rotating-shape shape-3" />
                </div >

        {/* Matrix rain effect */ }
        < div className = "absolute inset-0" >
        {
            Array.from({ length: 15 }, (_, i) => (
                <div
                    key={i}
                    className="matrix-column"
                    style={{
                        left: `${i * 7}%`,
                        animationDelay: `${i * 0.3}s`,
                        animationDuration: `${16 + Math.random() * 4}s`
                    }}
                >
                    <div className="matrix-char">⎡</div>
                    <div className="matrix-char">⎢</div>
                    <div className="matrix-char">⎣</div>
                </div>
            ))
        }
                </div >

        {/* Gradient overlays */ }
        < div className = "absolute inset-0 bg-gradient-to-t from-slate-900 via-transparent to-transparent z-28" />
            <div className="absolute inset-0 bg-gradient-to-b from-slate-900/50 via-transparent to-transparent z-28" />
              </div >
    )
}